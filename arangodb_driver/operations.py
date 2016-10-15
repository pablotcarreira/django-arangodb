import pickle

import datetime

from django.conf import settings
from django.db.backends.base.operations import BaseDatabaseOperations
from typing import Iterable


# TODO: Copy from django toolbox.
# Incui as operações específicas de conversão de tipos. Explicando melhor,
# o toolbox propõe que as conversões de tipos sejam centralizadas.
# https://www.allbuttonspressed.com/blog/django/2010/04/Writing-a-non-relational-Django-backend
class DatabaseOperations(BaseDatabaseOperations):
    """We mai need to implement other methods:

    * combine_expressions.



    """
    compiler_module = "arangodb_driver.compiler"

    def distinct_sql(self, fields: Iterable[str]) -> str:
        """Returns an SQL DISTINCT clause which removes duplicate rows from the
        result set. If any fields are given, only the given fields are being
        checked for duplicates.
        """
        if fields:
            raise NotImplementedError('DISTINCT ON fields is not supported by this database backend')
        else:
            return 'DISTINCT'

        # TODO: Implement distinc on multiple fields, must use COLLECT to do that:
            # https://www.arangodb.com/2015/07/return-distinct-in-aql/

        # if fields:
        #     return 'DISTINCT ON (%s)' % ', '.join(fields)
        # else:
        #     return 'DISTINCT'

    def get_db_converters(self, expression):
        """
                Get a list of functions needed to convert field data.

                Some field types on some backends do not provide data in the correct
                format, this is the hook for converter functions.
                """
        # TODO: Implement this for arangoDB
        return []


    def max_name_length(self) -> int:
        """Max lenght of collection name."""
        return 254

    def pk_default_value(self):
        """
        Returns None, to be interpreted by back-ends as a request to
        generate a new key for an "inserted" object.
        """
        return None

    def quote_name(self, name):
        """Does not do any quoting, as it is not needed for ArangoDB."""
        return name

    def prep_for_like_query(self, value):
        """Does no conversion, parent string-cast is SQL specific."""
        return value

    def year_lookup_bounds_for_date_field(self, value):
        """
        Converts year bounds to date bounds as these can likely be
        used directly, also adds one to the upper bound as it should be
        natural to use one strict inequality for BETWEEN-like filters
        for most nonrel back-ends.
        """
        first = datetime.date(value, 1, 1)
        second = datetime.date(value + 1, 1, 1)
        return [first, second]

