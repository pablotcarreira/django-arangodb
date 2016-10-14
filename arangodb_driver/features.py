from django.db.backends.base.features import BaseDatabaseFeatures


class DatabaseFeatures(BaseDatabaseFeatures):
    # Done:
    can_return_id_from_insert = True

    # TODO: Implement those features.
    # Check how cursors works and check compiler.execute_sql
    can_use_chunked_reads = True
    # Implement bulk insert.
    has_bulk_insert = True
    can_return_ids_from_bulk_insert = True
