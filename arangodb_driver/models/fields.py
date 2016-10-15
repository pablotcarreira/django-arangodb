# Pablo Carreira 2016
from django.db.models import Field


class ArangoDBField(Field):
    pass

class EdgeField:
    def __init__(self, other_model):
        self.other_model = other_model

class FromField(EdgeField):
    pass


class ToField(EdgeField):
    pass