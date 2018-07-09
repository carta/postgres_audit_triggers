from os.path import abspath, dirname, join
from django.db import migrations, models
import django.contrib.postgres.fields.hstore

BASE = join(abspath(dirname(__file__)), '..', 'sql')

with open(join(BASE, 'audit_0001.sql'), 'r') as f:
    sql = f.read()


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(sql),
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('event_id',
                 models.BigIntegerField(primary_key=True, serialize=False)),
                ('schema_name', models.TextField()),
                ('table_name', models.TextField()),
                ('relid', models.IntegerField()),
                ('session_user_name', models.TextField(null=True)),
                ('action_tstamp_tx', models.DateTimeField()),
                ('action_tstamp_stm', models.DateTimeField()),
                ('action_tstamp_clk', models.DateTimeField()),
                ('transaction_id', models.BigIntegerField(null=True)),
                ('application_name', models.TextField(null=True)),
                ('client_addr', models.GenericIPAddressField(null=True)),
                ('client_port', models.IntegerField(null=True)),
                ('client_query', models.TextField(null=True)),
                ('action', models.TextField()),
                ('row_data',
                 django.contrib.postgres.fields.hstore.HStoreField(null=True)),
                ('changed_fields',
                 django.contrib.postgres.fields.hstore.HStoreField(null=True)),
                ('statement_only', models.BooleanField()),
                ('metadata',
                 django.contrib.postgres.fields.hstore.HStoreField(null=True)),
            ],
            options={
                'db_table': '"audit"."logged_actions"',
                'managed': False,
            },
        ),
    ]
