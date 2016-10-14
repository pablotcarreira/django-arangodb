import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import DEFAULT_DB_ALIAS
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.base.validation import BaseDatabaseValidation
from django.db.utils import DatabaseError as WrappedDatabaseError
from django.utils import six
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.safestring import SafeBytes, SafeText


from arango import ArangoClient

from .client import DatabaseClient
from .features import DatabaseFeatures
from .operations import DatabaseOperations
from .creation import DatabaseCreation
from .introspection import DatabaseIntrospection
from .schema import DatabaseSchemaEditor
from typing import Mapping, List


class PythonArangoCursor(object):
    def __init__(self):
        """Simulates a cursor with methods required by Django."""
        pass

    def close(self):
        pass

    def execute(self, aql: str, params: Mapping) -> List:
        print(aql)
        print(params)

    def fetchmany(self, chunk_size):
        return []


class DatabaseWrapper(BaseDatabaseWrapper):
    # O arango suporta os seguintes primitivos:

    # null: An empty value, also: The absence of a value
    # bool: Boolean truth value with possible values false and true
    # number: Signed (real) number
    # string: UTF-8 encoded text value

    vendor = 'arangodb'
    queries_limit = 9000

    # Mapping of Field objects to their SQL suffix such as AUTOINCREMENT.
    data_types_suffix = {}
    # Mapping of Field objects to their SQL for CHECK constraints.
    data_type_check_constraints = {}
    ops = DatabaseOperations

    SchemaEditorClass = DatabaseSchemaEditor
    # Classes instantiated in __init__().
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
    validation_class = BaseDatabaseValidation

    # TODO: Copiado do postgres, verificar como fica no arangoDjango e no mongo.
    data_types = {
        'AutoField': 'serial',
        'CharField': 'varchar(%(max_length)s)',
        'BooleanField': 'boolean',
        'DecimalField': 'numeric(%(max_digits)s, %(decimal_places)s)',
        'array': 'array',  # arango
        'object': 'object', # arango
    }

    def _close(self):
        pass

    def get_connection_params(self):
        """Returns a dict of parameters suitable for get_new_connection.

        It's just a transformation and can be passed directly.

        :NOTE: Check for extra options.
        """
        # Copy from postgresql driver.
        settings_dict = self.settings_dict

        db_name = settings_dict.get('NAME', '')

        if db_name == '':
            raise ImproperlyConfigured(
                "settings.DATABASES is improperly configured. "
                "Please supply the NAME value.")

        conn_params = {
            'database': db_name,
        }

        # We will use that latter:
        self.database_name = settings_dict['NAME']

        conn_params.update(settings_dict['OPTIONS'])
        conn_params.pop('isolation_level', None)
        if settings_dict['USER']:
            conn_params['username'] = settings_dict['USER']
        if settings_dict['PASSWORD']:
            conn_params['password'] = force_str(settings_dict['PASSWORD'])
        if settings_dict['HOST']:
            conn_params['host'] = settings_dict['HOST']
        if settings_dict['PORT']:
            conn_params['port'] = settings_dict['PORT']
        return conn_params

    def get_new_connection(self, conn_params)->ArangoClient:
        """Opens a connection to the database.

        connection = ArangoClient(
            protocol='http',
            host='localhost',
            port=8529,
            username='root',
            password='',
            enable_logging=True)
        """
        database = conn_params.pop('database')
        connection = ArangoClient(**conn_params)
        database = connection.database(database)

        # FIXME: Very dangerous and not intuitive to set a database property here.
        # may be better to use an extra layer: A wrapper class that combine the functionality.
        self.database = database

        return connection

    def init_connection_state(self):
        """Initializes the database connection settings."""
        pass

    def create_cursor(self):
        """Creates a cursor. Assumes that a connection is established."""
        # FIXME: Wrap the query result cursor.
        return PythonArangoCursor()

    def _set_autocommit(self, autocommit):
        """
        Backend-specific implementation to enable or disable autocommit.
        """
        warnings.warn("_set_autocommit() not set", )

    def ensure_connection(self):
        """
        Guarantees that a connection to the database is established.
        """
        try:
            self.connection.verify()
        except AttributeError:
            self.connect()
            self.connection.verify()

    def set_autocommit(self, autocommit, force_begin_transaction_with_broken_autocommit=False):
        """
        Enable or disable autocommit.

        The usual way to start a transaction is to turn autocommit off.
        SQLite does not properly start a transaction when disabling
        autocommit. To avoid this buggy behavior and to actually enter a new
        transaction, an explcit BEGIN is required. Using
        force_begin_transaction_with_broken_autocommit=True will issue an
        explicit BEGIN with SQLite. This option will be ignored for other
        backends.
        """
        warnings.warn("set_autocommit() not set", )




