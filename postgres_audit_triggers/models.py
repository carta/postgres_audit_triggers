from django.db import models
from django.contrib.postgres.fields.hstore import HStoreField


class Audit(models.Model):
    event_id = models.BigIntegerField(primary_key=True)
    schema_name = models.TextField()
    table_name = models.TextField()
    relid = models.IntegerField()
    session_user_name = models.TextField(null=True)
    action_tstamp_tx = models.DateTimeField()
    action_tstamp_stm = models.DateTimeField()
    action_tstamp_clk = models.DateTimeField()
    transaction_id = models.BigIntegerField(null=True)
    application_name = models.TextField(null=True)
    client_addr = models.GenericIPAddressField(null=True)
    client_port = models.IntegerField(null=True)
    client_query = models.TextField(null=True)
    action = models.TextField()
    row_data = HStoreField(null=True)
    changed_fields = HStoreField(null=True)
    statement_only = models.BooleanField()
    metadata = HStoreField(null=True)

    class Meta:
        db_table = '"audit"."logged_actions"'
        managed = False
