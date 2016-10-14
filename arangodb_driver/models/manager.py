from django.db.models.manager import BaseManager
from .query import AQLQuerySet


class Manager(BaseManager.from_queryset(AQLQuerySet)):
    pass