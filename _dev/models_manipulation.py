# Pablo Carreira - 14/10/16

import django
django.setup()
# Create.
from sample_app.models import Person, Group


joao = Person(name='Joao')
a = joao.save()



print(a)
print(joao)
print(joao.pk)
print(type(joao.pk))

# TODO: Bulk insert


# grupo_patinadores = Group(name='Patinadores')
#
#
# # Connect.
# grupo_patinadores.members.add(joao)
