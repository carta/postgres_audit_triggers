from ast import literal_eval
import json

from rest_framework import serializers


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
    metadata = serializers.SerializerMethodField()

    def __parse_hfield(self, val):
        if val is None:
            return {}
        return val

    def __parse_dict(self, val):
        if isinstance(val, dict):
            return {k: self.__parse_dict(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [self.__parse_dict(v) for v in val]
        elif isinstance(val, str):
            try:
                return json.loads(val)
            except json.decoder.JSONDecodeError:
                try:
                    return literal_eval(val)
                except (ValueError, SyntaxError):
                    pass
        return val

    def get_row_data(self, obj):
        return self.__parse_hfield(obj.row_data)

    def get_changed_fields(self, obj):
        return self.__parse_hfield(obj.changed_fields)

    def get_metadata(self, obj):
        data = self.__parse_hfield(obj.metadata)
        return self.__parse_dict(data)
