from django.db.models.manager import BaseManager

from arangodb_driver.models.aql.query import AQLQuerySet


class ArangoDBManager(BaseManager.from_queryset(AQLQuerySet)):
    pass