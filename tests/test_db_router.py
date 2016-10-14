from unittest.mock import patch
from arangodb_driver.router import GraphRouter


class FakeSettings(object):
    DB_ROUTES = {'graph': 'arangodb'}
    DB_ROUTES_MODEL_TYPE_PROPERTY = 'model_type'
settings = FakeSettings()


class FakeModel(object):
    def __init__(self, type=None):
        self.model_type = type

class FakeModelUndefinedType(object):
    pass


@patch('arangodb_driver.router.settings', settings)
def test_router_class():
    router = GraphRouter()
    fake_arango_model = FakeModel('graph')
    fake_default_model_defined = FakeModel('default')
    fake_default_model_undefined = FakeModelUndefinedType()

    assert router.db_for_read(fake_arango_model) == 'arangodb'
    assert router.db_for_read(fake_default_model_defined) == 'default'
    assert router.db_for_read(fake_default_model_undefined) == 'default'



