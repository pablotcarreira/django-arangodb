from django.db.models import QuerySet
from django.db.models.expressions import Col
from django.db.models.query import ModelIterable
from django.db.models.sql import Query
from .where import AQLWhere


# FIXME: Nothing is bing done here, but the overrides are working and may be used.





class AQLQuery(Query):
    # compiler = 'AQLCompiler'
    def __init__(self, model, where=AQLWhere):
        super().__init__(model, where)


class AQLQuerySet(QuerySet):
    # noinspection PyMissingConstructor
    def __init__(self, model=None, query=None, using=None, hints=None):
        # Overriden in order to use our custom AQLQuery class.
        self.model = model
        self._db = using
        self._hints = hints or {}
        self.query = query or AQLQuery(self.model)
        self._result_cache = None
        self._sticky_filter = False
        self._for_write = False
        self._prefetch_related_lookups = []
        self._prefetch_done = False
        self._known_related_objects = {}  # {rel_field, {pk: rel_obj}}
        self._iterable_class = ModelIterable
        self._fields = None

    def __repr__(self):
        return "{} - Model: {}".format(self.__class__.__name__, self.model)

