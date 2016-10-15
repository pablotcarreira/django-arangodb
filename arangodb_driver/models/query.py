from django.db.models import QuerySet
from django.db.models.sql import Query
from django.db.models.sql.where import WhereNode


class AQLQuery(Query):
    compiler = 'AQLCompiler'


    def __init__(self, model, where=WhereNode):
        super().__init__(model, where)


class AQLQuerySet(QuerySet):
    def __repr__(self):
        return "{} - Model: {}".format(self.__class__.__name__, self.model)
