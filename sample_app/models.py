import os

from django.db import models

from arangodb_driver.models.models import NodeModel, EdgeModel


class Person(NodeModel):
    name = models.CharField(max_length=150)



