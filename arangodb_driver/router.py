from django.conf import settings


class GraphRouter(object):
    """
    A router to control graph models to be handled by ArangoDB.
    """
    def _route_by_model_type(self, model):
        model_type_property = getattr(settings, "DB_ROUTES_MODEL_TYPE_PROPERTY", 'model_type')
        model_type = getattr(model, model_type_property, 'default')
        if model_type == 'default' and 'default' not in settings.DB_ROUTES:
            # If not defined, "default" maps to "default".
            db_name = 'default'
        else:
           db_name = settings.DB_ROUTES[model_type]
        return db_name

    def db_for_read(self, model, **hints):
        return self._route_by_model_type(model)

    def db_for_write(self, model, **hints):
        return self._route_by_model_type(model)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models use the same database."""
        return self._route_by_model_type(obj1) == self._route_by_model_type(obj2)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """https://docs.djangoproject.com/en/1.10/topics/db/multi-db/#allow_migrate

        Avoid creating migrations on the graph database, that wouldn't work. Migrations
         for the graphdb uses a specific management command.
        """
        if db == 'arangodb':
            return False
        else:
            return True
