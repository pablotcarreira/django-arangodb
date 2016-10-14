from django.db.backends.base.features import BaseDatabaseFeatures



class DatabaseFeatures(BaseDatabaseFeatures):
    # Checked ArangoDB features:
    # TODO: Check how cursors works and check compiler.execute_sql
    can_use_chunked_reads = True


    can_return_id_from_insert = True

    # TODO: Doesn't seem necessary in general, move to back-ends.
    # TODO: Check arango docs.
    #       Mongo: see PyMongo's FAQ; GAE: see: http://timezones.appspot.com/.
    supports_date_lookup_using_string = False
    supports_timezones = False

    # Features that are commonly not available on nonrel databases.
    # TODO: Check that also
    supports_joins = False
    supports_select_related = False
    supports_deleting_related_objects = False

    # Having to decide whether to use an INSERT or an UPDATE query is
    # specific to SQL-based databases.
    # TODO: Check that also
    distinguishes_insert_from_update = False

    # Can primary_key be used on any field? Without encoding usually
    # only a limited set of types is acceptable for keys. This is a set
    # of all field kinds (internal_types) for which the primary_key
    # argument may be used.
    # TODO: Not in django features...
    # TODO: I believe that arangodb only has one PK. Need to check...
    # TODO: Use during model validation.
    # TODO: Move to core and use to skip unsuitable Django tests.
    # supports_primary_key_on = set(NonrelDatabaseCreation.data_types.keys()) - \
    #     set(('ForeignKey', 'OneToOneField', 'ManyToManyField', 'RawField',
    #          'AbstractIterableField', 'ListField', 'SetField', 'DictField',
    #          'EmbeddedModelField', 'BlobField'))

