from unittest.mock import patch

from django.core.management.commands import makemigrations
from django.db.migrations import autodetector, state

from ...operations import AddAuditTrigger, RemoveAuditTrigger

# HACK: add audit_trigger to available Meta options
state.DEFAULT_NAMES = state.DEFAULT_NAMES + (
    'audit_trigger',
)


class MigrationAutodetector(autodetector.MigrationAutodetector):
    def _detect_changes(self, convert_apps=None, graph=None):
        super()._detect_changes(convert_apps=convert_apps, graph=graph)
        self.altered_audit_triggers = {}
        self.create_altered_audit_triggers()
        self.generate_added_audit_triggers()
        self.generate_removed_audit_triggers()

        # Re-run this code since we may have added/removed audit triggers
        self._sort_migrations()
        self._build_migration_list(graph)
        self._optimize_migrations()
        return self.migrations

    def create_altered_audit_triggers(self):
        option_name = AddAuditTrigger.option_name
        for app_label, model_name in sorted(self.kept_model_keys):
            old_model_name = self.renamed_models.get(
                (app_label, model_name),
                model_name,
            )
            old_model_state = self.from_state.models[app_label, old_model_name]
            new_model_state = self.to_state.models[app_label, model_name]

            old_audit_trigger = old_model_state.options.get(option_name, False)
            new_audit_trigger = new_model_state.options.get(option_name, False)
            add_trigger = new_audit_trigger and not old_audit_trigger
            rem_trigger = old_audit_trigger and not new_audit_trigger

            self.altered_audit_triggers.update({
                (app_label, model_name): {
                    'added_audit_trigger': add_trigger,
                    'removed_audit_trigger': rem_trigger,
                }
            })

    def generate_added_audit_triggers(self):
        for (app_label, model_name), tr in self.altered_audit_triggers.items():
            if tr['added_audit_trigger']:
                self.add_operation(
                    app_label,
                    AddAuditTrigger(model_name),
                )

    def generate_removed_audit_triggers(self):
        for (app_label, model_name), tr in self.altered_audit_triggers.items():
            if tr['removed_audit_trigger']:
                self.add_operation(
                    app_label,
                    RemoveAuditTrigger(model_name),
                )


class Command(makemigrations.Command):
    """
    Since the MigrationAutodetector isn't extensible, patch the instance with
    our custom autodetector.
    """

    @patch(
        'django.core.management.commands.makemigrations.MigrationAutodetector',
        new=MigrationAutodetector,
    )
    def handle(self, *app_labels, **options):
        return super().handle(*app_labels, **options)
