from django.core.exceptions import EmptyResultSet
from django.db import DatabaseError
from django.db.models.sql.compiler import SQLCompiler as BaseCompiler, cursor_iter
from django.db.models.sql.constants import MULTI, NO_RESULTS, CURSOR, SINGLE
from django.db.transaction import TransactionManagementError

from arangodb_driver.models.query import AQLQuery


class SQLCompiler(BaseCompiler):
    query_class = AQLQuery
    query = AQLQuery

    def as_sql(self, with_limits=True, with_col_aliases=False, subquery=False):
        """
        Creates the SQL for this query. Returns the SQL string and list of
        parameters.

        If 'with_limits' is False, any limit/offset information is not included
        in the query.
        """
        ITEM_ALIAS = 'item'  # Alias for each item in the 'FOR ITEM_ALIAS IN'..


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

            if where:
                result.append('WHERE %s' % where)
                params.extend(w_params)

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

            return ' '.join(result), tuple(params)
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

        # TODO: Ponto onde podem ser inderidas as bind vars:
        # https://docs.arangodb.com/3.0/AQL/Fundamentals/BindParameters.html#bind-parameters
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


    def results_iter(self, results=None):
        """
        Returns an iterator over the results from executing this query.
        """
        converters = None
        if results is None:
            results = self.execute_sql(MULTI)
        fields = [s[0] for s in self.select[0:self.col_count]]
        converters = self.get_converters(fields)
        for rows in results:
            for row in rows:
                if converters:
                    row = self.apply_converters(row, converters)
                yield row




class SQLInsertCompiler(SQLCompiler):

    def __init__(self, *args, **kwargs):
        self.return_id = False
        super(SQLInsertCompiler, self).__init__(*args, **kwargs)

    def field_as_sql(self, field, val):
        """
        Take a field and a value intended to be saved on that field, and
        return placeholder SQL and accompanying params. Checks for raw values,
        expressions and fields with get_placeholder() defined in that order.

        When field is None, the value is considered raw and is used as the
        placeholder, with no corresponding parameters returned.
        """
        if field is None:
            # A field value of None means the value is raw.
            sql, params = val, []
        elif hasattr(val, 'as_sql'):
            # This is an expression, let's compile it.
            sql, params = self.compile(val)
        elif hasattr(field, 'get_placeholder'):
            # Some fields (e.g. geo fields) need special munging before
            # they can be inserted.
            sql, params = field.get_placeholder(val, self, self.connection), [val]
        else:
            # Return the common case for the placeholder
            sql, params = '%s', [val]

        # The following hook is only used by Oracle Spatial, which sometimes
        # needs to yield 'NULL' and [] as its placeholder and params instead
        # of '%s' and [None]. The 'NULL' placeholder is produced earlier by
        # OracleOperations.get_geom_placeholder(). The following line removes
        # the corresponding None parameter. See ticket #10888.
        params = self.connection.ops.modify_insert_params(sql, params)

        return sql, params

    def prepare_value(self, field, value):
        """
        Prepare a value to be used in a query by resolving it if it is an
        expression and otherwise calling the field's get_db_prep_save().
        """
        if hasattr(value, 'resolve_expression'):
            value = value.resolve_expression(self.query, allow_joins=False, for_save=True)
            # Don't allow values containing Col expressions. They refer to
            # existing columns on a row, but in the case of insert the row
            # doesn't exist yet.
            if value.contains_column_references:
                raise ValueError(
                    'Failed to insert expression "%s" on %s. F() expressions '
                    'can only be used to update, not to insert.' % (value, field)
                )
            if value.contains_aggregate:
                raise FieldError("Aggregate functions are not allowed in this query")
        else:
            value = field.get_db_prep_save(value, connection=self.connection)
        return value

    def pre_save_val(self, field, obj):
        """
        Get the given field's value off the given obj. pre_save() is used for
        things like auto_now on DateTimeField. Skip it if this is a raw query.
        """
        if self.query.raw:
            return getattr(obj, field.attname)
        return field.pre_save(obj, add=True)

    def assemble_as_sql(self, fields, value_rows):
        """
        Take a sequence of N fields and a sequence of M rows of values,
        generate placeholder SQL and parameters for each field and value, and
        return a pair containing:
         * a sequence of M rows of N SQL placeholder strings, and
         * a sequence of M rows of corresponding parameter values.

        Each placeholder string may contain any number of '%s' interpolation
        strings, and each parameter row will contain exactly as many params
        as the total number of '%s's in the corresponding placeholder row.
        """
        if not value_rows:
            return [], []

        # list of (sql, [params]) tuples for each object to be saved
        # Shape: [n_objs][n_fields][2]
        rows_of_fields_as_sql = (
            (self.field_as_sql(field, v) for field, v in zip(fields, row))
            for row in value_rows
        )

        # tuple like ([sqls], [[params]s]) for each object to be saved
        # Shape: [n_objs][2][n_fields]
        sql_and_param_pair_rows = (zip(*row) for row in rows_of_fields_as_sql)

        # Extract separate lists for placeholders and params.
        # Each of these has shape [n_objs][n_fields]
        placeholder_rows, param_rows = zip(*sql_and_param_pair_rows)

        # Params for each field are still lists, and need to be flattened.
        param_rows = [[p for ps in row for p in ps] for row in param_rows]

        return placeholder_rows, param_rows

    def as_sql(self):
        # We don't need quote_name_unless_alias() here, since these are all
        # going to be column names (so we can avoid the extra overhead).
        qn = self.connection.ops.quote_name
        opts = self.query.get_meta()
        result = ['INSERT INTO %s' % qn(opts.db_table)]

        has_fields = bool(self.query.fields)
        fields = self.query.fields if has_fields else [opts.pk]
        result.append('(%s)' % ', '.join(qn(f.column) for f in fields))

        if has_fields:
            value_rows = [
                [self.prepare_value(field, self.pre_save_val(field, obj)) for field in fields]
                for obj in self.query.objs
            ]
        else:
            # An empty object.
            value_rows = [[self.connection.ops.pk_default_value()] for _ in self.query.objs]
            fields = [None]

        # Currently the backends just accept values when generating bulk
        # queries and generate their own placeholders. Doing that isn't
        # necessary and it should be possible to use placeholders and
        # expressions in bulk inserts too.
        can_bulk = (not self.return_id and self.connection.features.has_bulk_insert)

        placeholder_rows, param_rows = self.assemble_as_sql(fields, value_rows)

        if self.return_id and self.connection.features.can_return_id_from_insert:
            if self.connection.features.can_return_ids_from_bulk_insert:
                result.append(self.connection.ops.bulk_insert_sql(fields, placeholder_rows))
                params = param_rows
            else:
                result.append("VALUES (%s)" % ", ".join(placeholder_rows[0]))
                params = [param_rows[0]]
            col = "%s.%s" % (qn(opts.db_table), qn(opts.pk.column))
            r_fmt, r_params = self.connection.ops.return_insert_id()
            # Skip empty r_fmt to allow subclasses to customize behavior for
            # 3rd party backends. Refs #19096.
            if r_fmt:
                result.append(r_fmt % col)
                params += [r_params]
            return [(" ".join(result), tuple(chain.from_iterable(params)))]

        if can_bulk:
            result.append(self.connection.ops.bulk_insert_sql(fields, placeholder_rows))
            return [(" ".join(result), tuple(p for ps in param_rows for p in ps))]
        else:
            return [
                (" ".join(result + ["VALUES (%s)" % ", ".join(p)]), vals)
                for p, vals in zip(placeholder_rows, param_rows)
            ]

    def execute_sql(self, return_id=False)->int:
        # self.fields contem os fields para serem adicionados.
        print(self)
