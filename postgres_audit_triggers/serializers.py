from uuid import UUID
import json

from rest_framework import serializers

from django.apps.registry import apps


class AuditSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    schema_name = serializers.CharField()
    table_name = serializers.CharField()
    relid = serializers.IntegerField()
    session_user_name = serializers.CharField(allow_null=True)
    action_tstamp_tx = serializers.DateTimeField()
    action_tstamp_stm = serializers.DateTimeField()
    action_tstamp_clk = serializers.DateTimeField()
    transaction_id = serializers.IntegerField(allow_null=True)
    application_name = serializers.CharField(allow_null=True)
    client_addr = serializers.IPAddressField(allow_null=True)
    client_port = serializers.IntegerField(allow_null=True)
    client_query = serializers.CharField(allow_null=True)
    action = serializers.CharField()
    row_data = serializers.SerializerMethodField()
    changed_fields = serializers.SerializerMethodField()
    statement_only = serializers.BooleanField()
    metadata = serializers.JSONField(
        initial=dict,
        required=False,
    )

    def __clean_val(self, table_name, key, val):
        val = val.strip('"').replace('\\', '')
        if val == 'NULL':
            return None
        elif key == 'reference_id':
            return UUID(val)
        elif key.endswith('id') and key != 'individual_id':
            return int(val)
        elif key == 'metadata':
            return json.loads(val)
        Model = apps.get_model(*table_name.rsplit('_', 1))
        return Model._meta.get_field(key).to_python(val)

    def __parse_hfield(self, table_name, val):
        if val is None:
            return {}
        return val

    def get_row_data(self, obj):
        return self.__parse_hfield(obj.table_name, obj.row_data)

    def get_changed_fields(self, obj):
        return self.__parse_hfield(obj.table_name, obj.changed_fields)
