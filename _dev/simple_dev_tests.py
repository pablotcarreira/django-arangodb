import os

from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sample_project.settings")

import django
print("Django Version: " + django.__version__)
django.setup()


call_command('migrate')
# call_command('makemigrations')
