from django.db import models
from django.db.models.base import ModelBase

from arangodb_driver.models.fields import AutoField
from .arangodbmanager import ArangoDBManager


# If we want to make the base class more elegant, it's possible
# to override the _meta API: https://docs.djangoproject.com/pt-br/1.10/ref/models/meta/
# class DocumentModelOptions(Options):
#     pass
# class ArangoDBModelBase(ModelBase):
#     pass
# Meta override: http://kells.tj/blog/2014/11/06/renaming-djangos-autopk-field.html



class DocumentModel(models.Model):
    _key = AutoField(primary_key=True)
    objects = ArangoDBManager()
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

