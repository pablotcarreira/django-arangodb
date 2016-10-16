import os

from django.db import models

from arangodb_driver.models.fields import FromField, ToField, CharField, AutoField
from arangodb_driver.models.models import VertexModel, EdgeModel

# M2M Through
# https://docs.djangoproject.com/en/1.10/ref/models/fields/#django.db.models.ManyToManyField.through




class Person(VertexModel):
    name = CharField(max_length=150)
    age = models.IntegerField()


class Group(VertexModel):
    name = models.CharField(max_length=150)


class Belongs(EdgeModel):
    _from = FromField('Person')
    _to = ToField('Group')
    join_date = models.DateField()


if __name__ == '__main__':
    pass
    # We want to perform queries like:
    # Query relations.
    # my_groups = aperson.groups.all()
    # persons_in_a_group = agroup.persons.all()

    # Query Edges
    # for item in my_groups:
    #     print(item.join_date)

    # Or something like graphql (makes more sense).
    # my_group_edges = aperson.groups.all()
    # for edge in my_groups:
    #     print(edge.join_date)
    #     print(edge.group.name)





