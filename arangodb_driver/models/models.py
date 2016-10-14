from django.db.models import Model as DjangoModel
from .manager import Manager


class BaseGraphModel(DjangoModel):
    objects = Manager()
    model_type = 'graph'

    class Meta:
        abstract = True
        required_db_vendor = 'arangodb'


class NodeModel(BaseGraphModel):
    model_type = 'node'

    class Meta:
        abstract = True


class EdgeModel(BaseGraphModel):
    model_type = 'edge'

    class Meta:
        abstract = True

