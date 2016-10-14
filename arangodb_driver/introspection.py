from django.db.backends.base.introspection import BaseDatabaseIntrospection, TableInfo
from typing import List


class DatabaseIntrospection(BaseDatabaseIntrospection):
    def get_table_list(self, cursor)->List[TableInfo]:
        """Get the collections dict and return it as list of TableInfos"""
        collections = self.connection.database.collections()
        table_list = [TableInfo(c['name'], c['type']) for c in collections]
        return table_list


