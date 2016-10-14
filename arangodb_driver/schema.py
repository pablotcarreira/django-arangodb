from arango.exceptions import CollectionCreateError
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.models.base import ModelBase


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):

    def create_model(self, model: ModelBase):
        # TODO: Diferenciar se é edge collection.
        name = model._meta.db_table
        try:
            self.connection.database.create_collection(name, edge=False)
        except CollectionCreateError:
            print("Collection {} already exists.".format(name))


    def delete_model(self, model):
        raise NotImplementedError

