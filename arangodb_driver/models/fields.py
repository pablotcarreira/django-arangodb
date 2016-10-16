# Pablo Carreira 2016
from django.db import models



class IntegerField(models.IntegerField):
    pass


class CharField(models.CharField):
    def select_format(self, compiler, sql, params):
        # Copy of the default implementation just for reference.
        return sql, params

    def get_db_prep_value(self, value, connection, prepared:bool=False):
        """Returns field's value prepared for interacting with the database
        backend.

        Used by the default implementations of get_db_prep_save().
        """
        # We need to quote string fields.
        # I don't know how prepared works, but the lookup sends True.
        if prepared:
            value = '"' + str(value) + '"'
        return value


class EdgeField:
    def __init__(self, other_model):
        self.other_model = other_model

class FromField(EdgeField):
    pass


class ToField(EdgeField):
    pass