from django.db.models import Model as DjangoModel
from .manager import Manager


class DocumentModel(DjangoModel):
    objects = Manager()
    model_type = 'arangodb_document'

    class Meta:
        abstract = True
        required_db_vendor = 'arangodb'


class VertexModel(DocumentModel):
    model_type = 'arangodb_node'

    class Meta:
        abstract = True


class EdgeModel(DocumentModel):
    model_type = 'arangodb_edge'

    class Meta:
        abstract = True

