from django.db.migrations.operations.base import Operation
from django.utils.functional import cached_property


__all__ = (
    'AddAuditTrigger',
    'RemoveAuditTrigger',
)


class AddAuditTrigger(Operation):
    reduces_to_sql = True
    reversible = True
    option_name = 'audit_trigger'
    enabled = True

    def __init__(self, model_name):
        self.name = model_name

    @cached_property
    def model_name_lower(self):
        return self.name.lower()

    def state_forwards(self, app_label, state):
        model_state = state.models[app_label, self.model_name_lower]
        model_state.options[self.option_name] = self.enabled
        state.reload_model(app_label, self.model_name_lower, delay=True)

    def database_forwards(
        self, app_label, schema_editor, from_state, to_state,
    ):
        model = to_state.apps.get_model(app_label, self.name)
        table = model._meta.db_table
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('SELECT to_regclass(\'audit.logged_actions\')')
            has_audit = cursor.fetchone()[0]
        if has_audit:
            schema_editor.execute(
                'SELECT audit.audit_table(\'{}\')'.format(table),
            )

    def database_backwards(
        self, app_label, schema_editor, from_state, to_state,
    ):
        model = to_state.apps.get_model(app_label, self.name)
        table = model._meta.db_table
        schema_editor.execute(
            'DROP TRIGGER IF EXISTS audit_trigger_row ON {}'.format(table),
        )
        schema_editor.execute(
            'DROP TRIGGER IF EXISTS audit_trigger_stm ON {}'.format(table),
        )

    def describe(self):
        return 'Add audit triggers on model {}'.format(self.name)


class RemoveAuditTrigger(AddAuditTrigger):
    enabled = False

    def database_forwards(
        self, app_label, schema_editor, from_state, to_state,
    ):
        super().database_backwards(
            app_label, schema_editor, from_state, to_state,
        )

    def database_backwards(
        self, app_label, schema_editor, from_state, to_state,
    ):
        super().database_forwards(
            app_label, schema_editor, from_state, to_state,
        )

    def describe(self):
        return 'Remove audit triggers on model {}'.format(self.name)
