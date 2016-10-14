# Pablo Carreira - 14/10/16

import django
django.setup()
# Create.
from sample_app.models import Person, Group


joao = Person(name='Joao')
joao.save()
# grupo_patinadores = Group(name='Patinadores')
#
#
# # Connect.
# grupo_patinadores.members.add(joao)
