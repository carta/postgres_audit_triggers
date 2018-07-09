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
        # This is copied straight from the super class except where noted

        # The first phase is generating all the operations for each app
        # and gathering them into a big per-app list.
        # Then go through that list, order it, and split into migrations to
        # resolve dependencies caused by M2Ms and FKs.
        self.generated_operations = {}
        self.altered_indexes = {}

        # Prepare some old/new state and model lists, separating
        # proxy models and ignoring unmigrated apps.
        self.old_apps = self.from_state.concrete_apps
        self.new_apps = self.to_state.apps
        self.old_model_keys = set()
        self.old_proxy_keys = set()
        self.old_unmanaged_keys = set()
        self.new_model_keys = set()
        self.new_proxy_keys = set()
        self.new_unmanaged_keys = set()
        for al, mn in self.from_state.models:
            model = self.old_apps.get_model(al, mn)
            if not model._meta.managed:
                self.old_unmanaged_keys.add((al, mn))
            elif al not in self.from_state.real_apps:
                if model._meta.proxy:
                    self.old_proxy_keys.add((al, mn))
                else:
                    self.old_model_keys.add((al, mn))

        for al, mn in self.to_state.models:
            model = self.new_apps.get_model(al, mn)
            if not model._meta.managed:
                self.new_unmanaged_keys.add((al, mn))
            elif (
                al not in self.from_state.real_apps or
                (convert_apps and al in convert_apps)
            ):
                if model._meta.proxy:
                    self.new_proxy_keys.add((al, mn))
                else:
                    self.new_model_keys.add((al, mn))

        # Renames have to come first
        self.generate_renamed_models()

        # Prepare lists of fields and generate through model map
        self._prepare_field_lists()
        self._generate_through_model_map()

        # Generate non-rename model operations
        self.generate_deleted_models()
        self.generate_created_models()
        self.generate_deleted_proxies()
        self.generate_created_proxies()
        self.generate_altered_options()
        self.generate_altered_managers()

        # Create the altered indexes and store them in self.altered_indexes.
        # This avoids the same computation in generate_removed_indexes()
        # and generate_added_indexes().
        self.create_altered_indexes()
        # Generate index removal operations before field is removed
        self.generate_removed_indexes()

        # CUSTOM:
        self.altered_audit_triggers = {}
        self.create_altered_audit_triggers()
        self.generate_added_audit_triggers()
        self.generate_removed_audit_triggers()

        # Generate field operations
        self.generate_renamed_fields()
        self.generate_removed_fields()
        self.generate_added_fields()
        self.generate_altered_fields()
        self.generate_altered_unique_together()
        self.generate_altered_index_together()
        self.generate_added_indexes()
        self.generate_altered_db_table()
        self.generate_altered_order_with_respect_to()

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
