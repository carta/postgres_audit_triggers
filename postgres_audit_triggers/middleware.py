import json

from django.contrib.postgres.fields.hstore import HStoreField
from django.db import connection
from django.utils.deprecation import MiddlewareMixin


class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        hstore = HStoreField()
        meta_str = request.META.pop('HTTP_POSTGRES_AUDIT_TRIGGERS_META', '{}')
        try:
            meta = hstore.get_db_prep_save(json.loads(meta_str), connection)
        except json.decoder.JSONDecodeError:
            meta = {}
        if not meta:
            return
        commands = (
            ('CREATE TEMP TABLE IF NOT EXISTS '
             '"_app_metadata" (metadata hstore)', ()),
            ('UPDATE _app_metadata SET metadata=hstore(%s)', (meta,)),
            ('INSERT INTO _app_metadata (metadata) '
             'SELECT %s WHERE NOT EXISTS (SELECT metadata FROM _app_metadata)',
             (meta,)),
        )
        with connection.cursor() as cursor:
            for command, params in commands:
                cursor.execute(command, params)
