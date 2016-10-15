# Pablo Carreira - 15/10/16
from django.db.models.sql.where import WhereNode

# FIXME: Nothing is bing done here, but the overrides are working and may be used.

class AQLWhere(WhereNode):
    def as_sql(self, compiler, connection):
        return super(AQLWhere, self).as_sql(compiler, connection)

