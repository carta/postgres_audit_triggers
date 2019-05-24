# Generated by Django 2.2.1 on 2019-05-23 23:09

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('postgres_audit_triggers', '0004_indexes'),
    ]

    operations = [
        migrations.RunSQL(
            'CREATE INDEX CONCURRENTLY postgres_a_table_n_745812_idx ON audit.logged_actions(table_name)',
        ),
        migrations.RunSQL(
            'CREATE INDEX CONCURRENTLY postgres_a_action__d42ba2_idx ON audit.logged_actions(action_tstamp_tx)',
        ),
        migrations.RunSQL(
            'CREATE INDEX CONCURRENTLY postgres_a_action_116cf9_idx ON audit.logged_actions(action)',
        ),
    ]
