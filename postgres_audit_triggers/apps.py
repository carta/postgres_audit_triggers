from django.apps import AppConfig
from django.db.models import options

# HACK: add audit_trigger to available Meta options
options.DEFAULT_NAMES = options.DEFAULT_NAMES + (
    'audit_trigger',
)


class AuditConfig(AppConfig):
    name = 'postgres_audit_triggers'

    def ready(self):
        pass
