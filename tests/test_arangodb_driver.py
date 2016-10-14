import os
import warnings

import arango
import pytest
import requests
from arango import ArangoClient, exceptions
from django.core.management import call_command
from django.db.backends.base.base import BaseDatabaseWrapper

from arangodb_driver import base


def test_instance():
    settings_dict = {
    }

    driver = base.DatabaseWrapper(settings_dict)
    assert isinstance(driver, BaseDatabaseWrapper)

def test_connection_fail():
    settings_dict_wrong_user = {
        'NAME': 'teste_python',
        'ENGINE': 'django-arango-driver',
        'TIME_ZONE': None,
        'CONN_MAX_AGE': None,
        'OPTIONS': (),
        'USER': 'fake_user',
        'PORT': '8529',
        'PASSWORD': 'omoomo',
        'HOST': 'localhost',
        'AUTOCOMMIT': True,
    }
    settings_dict_wrong_port = {
        'NAME': 'teste_python',
        'ENGINE': 'django-arango-driver',
        'TIME_ZONE': None,
        'CONN_MAX_AGE': None,
        'OPTIONS': (),
        'USER': 'fake_user',
        'PORT': '5555',
        'PASSWORD': 'omoomo',
        'HOST': 'localhost',
        'AUTOCOMMIT': True,
    }
    driver = base.DatabaseWrapper(settings_dict_wrong_user)
    driver.connect()
    assert isinstance(driver.connection, ArangoClient)
    with pytest.raises(arango.exceptions.ServerConnectionError):
        driver.ensure_connection()

    driver = base.DatabaseWrapper(settings_dict_wrong_port)
    driver.connect()
    assert isinstance(driver.connection, ArangoClient)
    with pytest.raises(requests.exceptions.ConnectionError):
        driver.ensure_connection()


def test_connection_ok():
    settings_dict = {
        'NAME': 'teste_python',
        'ENGINE': 'django-arango-driver',
        'TIME_ZONE': None,
        'CONN_MAX_AGE': None,
        'OPTIONS': (),
        'USER': 'root',
        'PORT': '8529',
        'PASSWORD': 'omoomo',
        'HOST': 'localhost',
        'AUTOCOMMIT': True,
    }
    warnings.warn("Root user used in tests.")
    driver = base.DatabaseWrapper(settings_dict)
    driver.connect()
    assert isinstance(driver.connection, ArangoClient)
    driver.ensure_connection()


def test_start_django_app():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sample_project.settings")
    import django
    django.setup()


def test_make_migrations():
    call_command('makemigrations')

