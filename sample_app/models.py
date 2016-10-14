import os

from django.db import models

from arangodb_driver.models.fields import FromField, ToField
from arangodb_driver.models.models import VertexModel, EdgeModel


class Person(VertexModel):
    name = models.CharField(max_length=150)


class Group(VertexModel):
    name = models.CharField(max_length=150)


class Belongs(EdgeModel):
    _from = FromField('Person')
    _to = ToField('Group')
    join_date = models.DateField()




