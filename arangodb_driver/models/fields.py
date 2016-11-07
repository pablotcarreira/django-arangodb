# Pablo Carreira 2016
from django.db import models


def quote_string(value: str) -> str:
    """Quote a string in order to compose an AQL query."""
    return '"' + str(value) + '"'


class IntegerField(models.IntegerField):
    pass


class AutoField(models.AutoField):
    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
            value = connection.ops.validate_autopk_value(value)
        else:
            value = quote_string(value)
        return value


class CharField(models.CharField):
    def get_db_prep_value(self, value, connection, prepared: bool = False):
        # We need to quote string fields.
        # I don't know how prepared works, but the lookup sends True.
        if prepared:
            value = quote_string(value)
        return value


class EdgeField:
    def __init__(self, other_model):
        self.other_model = other_model


class FromField(EdgeField):
    pass


class ToField(EdgeField):
    pass


class ManyToMany(models.ManyToManyField):
    pass