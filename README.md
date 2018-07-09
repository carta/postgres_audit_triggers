Postgres audit database via triggers
====================================

This app sets up a postgres audit database via triggers.
See https://wiki.postgresql.org/wiki/Audit_trigger_91plus
and https://github.com/2ndQuadrant/audit-trigger/
for more information.


Installation
============
`pip install postgres_audit_triggers`


Usage
=====

- Add the `postgres_audit_triggers` app to `INSTALLED_APPS` *before* any apps that will be audited:

```
# settings.py
INSTALLED_APPS = {
    'django.contrib.postgres',
    'postgres_audit_triggers',
    ...
}
```

- Install the `postgres_audit_triggers` middleware:

```
# settings.py
MIDDLEWARE = [
    ...
    'postgres_audit_triggers.middleware.AuditMiddleware',
]
```

This middleware will add metadata to the audit row. To send metadata, the client must send a
`Postgres-Audit-Triggers-Meta` header in the request to your Django view. The data within
that header must be JSON serializable to a python dictionary.

- Run migrations: `python manage.py migrate postgres_audit_triggers`

- Add `audit_trigger = True` to the Model Meta options of the models that will be audited:

```
# models.py
class MyAuditedModel(models.Model):
    ...
    class Meta:
        audit_trigger = True
        ...
```

- Make migrations: `python manage.py makemigrations`
- Run migrations: `python manage.py migrate`

Triggers introduce performance overhead. In certain cases, you may need to disable triggers while
performing bulk operations. To turn off all triggers, a decorator is provided:

```
from postgres_audit_triggers.decorators import disable_triggers


@disable_triggers
def foo():
    # auditing will not be triggered on any database operations performed here
    Bar.objects.bulk_create(items)
```
