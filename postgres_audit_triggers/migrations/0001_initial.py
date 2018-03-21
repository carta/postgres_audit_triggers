from os.path import abspath, dirname, join
from django.db import migrations

with open(join(abspath(dirname(__file__)), '..', 'audit.sql'), 'r') as f:
    sql = f.read()


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(sql),
    ]
