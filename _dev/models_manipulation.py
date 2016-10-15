# Pablo Carreira - 14/10/16

import django
django.setup()
# Create.
from sample_app.models import Person, Group

# INSERT
# joao = Person(name='Joao')
# a = joao.save()

# GET
aperson = Person.objects.get(pk='478589')
print(aperson)

# grupo_patinadores = Group(name='Patinadores')
#
#
# # Connect.
# grupo_patinadores.members.add(joao)
