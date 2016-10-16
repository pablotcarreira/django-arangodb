import json
from typing import List

from django.core.exceptions import EmptyResultSet
from django.db import DatabaseError
from django.db import IntegrityError
from django.db.models import NOT_PROVIDED
from django.db.models.expressions import Col
from django.db.models.sql import compiler
from django.db.models.sql.constants import MULTI, NO_RESULTS, CURSOR, SINGLE
from django.db.transaction import TransactionManagementError

from arangodb_driver.defines import ITEM_ALIAS
from arangodb_driver.models.aql.query import AQLQuery



# Patch the Col expression so it returns the column formatted by AQL standards.
def override_col_as_sql(self, compiler, connection) -> (str, List):
    """
    Responsible for returning a (sql, [params]) tuple to be included
    in the current query.

    Different backends can provide their own implementation, by
    providing an `as_{vendor}` method and patching the Expression:

    ```
    def override_as_sql(self, compiler, connection):
        # custom logic
        return super(Expression, self).as_sql(compiler, connection)
    setattr(Expression, 'as_' + connection.vendor, override_as_sql)
    """
    return "%s.%s" % (ITEM_ALIAS, self.target.column), []
setattr(Col, 'as_arangodb', override_col_as_sql)




class SQLCompiler(compiler.SQLCompiler):
    query_class = AQLQuery




    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        """
        Creates the SQL for this query. Returns the SQL string and list of
        parameters.

        If 'with_limits' is False, any limit/offset information is not included
        in the query.
        """
        self.subquery = subquery
        refcounts_before = self.query.alias_refcount.copy()

        try:
            extra_select, order_by, group_by = self.pre_sql_setup()
            distinct_fields = self.get_distinct()
            from_, f_params = self.get_from_clause()
            where, w_params = self.compile(self.where) if self.where is not None else ("", [])
            having, h_params = self.compile(self.having) if self.having is not None else ("", [])

            params = []
            result = ['FOR', ITEM_ALIAS, 'IN']
            result.extend(from_)

            # Append the FILTER (sql where).
            if where:
                result.append('FILTER')
                # quoted_params = quote_params(w_params)
                # where_partial = where % tuple(quoted_params)
                where_partial = where % tuple(w_params)
                result.append(where_partial)

                # result.append('FILTER %s ' % where % '"%s"' % w_params[0])  # FIXME: Looks like a hack right now...
                params.extend(w_params)

            result.append('RETURN')

            if self.query.distinct:
                result.append(self.connection.ops.distinct_sql(distinct_fields))

            out_cols = {}
            col_idx = 1

            for _, (s_sql, s_params), alias in self.select + extra_select:
                if alias:
                    s_sql = '%s AS %s' % (s_sql, self.connection.ops.quote_name(alias))
                elif with_col_aliases:
                    s_sql = '%s AS %s' % (s_sql, 'Col%d' % col_idx)
                    col_idx += 1
                params.extend(s_params)

                # Prepare the dict output ITEM_ALIAS.
                field_name = s_sql.split('.')[1]  # TODO: The alias is used here.
                prepared_s_sql = ITEM_ALIAS + '.' + field_name
                out_cols[field_name] = prepared_s_sql

            # Transform the dict into a AQL return object.
            out_cols = str(out_cols).replace("'", "")
            result.append(out_cols)
            params.extend(f_params)

            for_update_part = None
            if self.query.select_for_update and self.connection.features.has_select_for_update:
                if self.connection.get_autocommit():
                    raise TransactionManagementError("select_for_update cannot be used outside of a transaction.")

                nowait = self.query.select_for_update_nowait
                skip_locked = self.query.select_for_update_skip_locked
                # If it's a NOWAIT/SKIP LOCKED query but the backend doesn't
                # support it, raise a DatabaseError to prevent a possible
                # deadlock.
                if nowait and not self.connection.features.has_select_for_update_nowait:
                    raise DatabaseError('NOWAIT is not supported on this database backend.')
                elif skip_locked and not self.connection.features.has_select_for_update_skip_locked:
                    raise DatabaseError('SKIP LOCKED is not supported on this database backend.')
                for_update_part = self.connection.ops.for_update_sql(nowait=nowait, skip_locked=skip_locked)

            if for_update_part and self.connection.features.for_update_after_from:
                result.append(for_update_part)



            grouping = []
            for g_sql, g_params in group_by:
                grouping.append(g_sql)
                params.extend(g_params)
            if grouping:
                if distinct_fields:
                    raise NotImplementedError(
                        "annotate() + distinct(fields) is not implemented.")
                if not order_by:
                    order_by = self.connection.ops.force_no_ordering()
                result.append('GROUP BY %s' % ', '.join(grouping))

            if having:
                result.append('HAVING %s' % having)
                params.extend(h_params)

            if order_by:
                ordering = []
                for _, (o_sql, o_params, _) in order_by:
                    ordering.append(o_sql)
                    params.extend(o_params)
                result.append('ORDER BY %s' % ', '.join(ordering))

            if with_limits:
                if self.query.high_mark is not None:
                    result.append('LIMIT %d' % (self.query.high_mark - self.query.low_mark))
                if self.query.low_mark:
                    if self.query.high_mark is None:
                        val = self.connection.ops.no_limit_value()
                        if val:
                            result.append('LIMIT %d' % val)
                    result.append('OFFSET %d' % self.query.low_mark)

            if for_update_part and not self.connection.features.for_update_after_from:
                result.append(for_update_part)

            result = ' '.join(result), tuple(params)
            return result
        finally:
            # Finally do cleanup - get rid of the joins we created above.
            self.query.reset_refcounts(refcounts_before)

    def execute_sql(self, result_type=MULTI):
        """
        Run the query against the database and returns the result(s). The
        return value is a single data item if result_type is SINGLE, or an
        iterator over the results if the result_type is MULTI.

        result_type is either MULTI (use fetchmany() to retrieve all rows),
        SINGLE (only retrieve a single row), or None. In this last case, the
        cursor is returned if any query is executed, since it's used by
        subclasses such as InsertQuery). It's possible, however, that no query
        is needed, as the filters describe an empty set. In that case, None is
        returned, to avoid any unnecessary database interaction.

        ----
        # https://docs.arangodb.com/3.0/AQL/Fundamentals/BindParameters.html#bind-parameters
        ----

        """
        if not result_type:
            result_type = NO_RESULTS
        try:
            sql, params = self.as_sql()
            if not sql:
                raise EmptyResultSet
        except EmptyResultSet:
            if result_type == MULTI:
                return iter([])
            else:
                return


        self.connection.ensure_connection()

        cursor = self.connection.database.aql.execute(query=sql)
        if result_type == CURSOR:
            # Caller didn't specify a result_type, so just give them back the
            # cursor to process (and close).
            return cursor
        if result_type == SINGLE:
            try:
                return cursor.next()
            finally:
                # done with the cursor
                cursor.close()
        if result_type == NO_RESULTS:
            cursor.close()
            return

        # TODO: Fazer a relação do cursor com o batch (quantos elementos são pegos por vez).
        # result = cursor_iter(
        #     cursor, self.connection.features.empty_fetchmany_value,
        #     self.col_count
        # )
        result = cursor.batch()

        if not self.connection.features.can_use_chunked_reads:
            try:
                # If we are using non-chunked reads, we return the same data
                # structure as normally, but ensure it is all read into memory
                # before going any further.
                return list(result)
            finally:
                # done with the cursor
                cursor.close()
        return result

    def _make_result(self, entity, fields):
        """
        Decodes values for the given fields from the database entity.

        The entity is assumed to be a dict using field database column
        names as keys. Decodes values using `value_from_db` as well as
        the standard `convert_values`.
        """
        result = []
        for field in fields:
            value = entity.get(field.target.column, None)
            result.append(value)
        return result

    def results_iter(self, results=None):
        # Results are dictionaries and we can't trust the order of the fields. This part deal with that.
        if results is None:
            results = self.execute_sql(MULTI)
        fields = [s[0] for s in self.select[0:self.col_count]]
        new_result = []
        for item in results:
            new_result.append(self._make_result(item, fields))

        # Now we return to the default django execution.
        converters = self.get_converters(fields)
        for row in new_result:
            if converters:
                row = self.apply_converters(row, converters)
            yield row


class SQLInsertCompiler(SQLCompiler, compiler.SQLInsertCompiler):
    return_id = True

    def execute_sql(self, return_id=True):
        # Implemented in order to use the universal execute SQL.
        ids = super().execute_sql(MULTI)
        if len(ids) == 1:
            return ids[0]
        else:
            return ids

    # noinspection PyMethodOverriding
    def as_sql(self):
        """Arango INSERT has the following format:

            FOR item IN [{"nome":"B"}, {"nome":"C"}]
                INSERT item IN Usuario
                RETURN NEW._key

        It's naturally bulk.
        """
        opts = self.query.get_meta()
        collection_name = opts.db_table
        result = ['FOR', ITEM_ALIAS, 'IN']
        has_fields = bool(self.query.fields)
        fields = self.query.fields if has_fields else [opts.pk]
        documents = []
        if has_fields:
            # Prepare the dictionary for insertion.
            for obj in self.query.objs:
                document = {}
                for field in fields:
                    document[field.column] = self.prepare_value(field, self.pre_save_val(field, obj))
                documents.append(document)
        else:
            # An empty object.
            documents.append('{}')
        # Complete the query statement.
        result.append(json.dumps(documents))
        result.extend(('INSERT', ITEM_ALIAS, 'IN', collection_name, 'RETURN NEW._key'))
        # All inserts return ids, for this on the class because I don't know if Django uses it.
        # self.return_id = True
        # Empty params in this case.
        result = " ".join(result)

        return result, ()
