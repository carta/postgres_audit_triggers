from django.db import transaction


def disable_triggers(func, using=None):
    """
    Disables all triggers before executing the function.
    Useful when performing bulk operations which don't
    require auditing to be performed.
    """
    def _inner(*args, **kwargs):
        connection = transaction.get_connection(using=using)
        with connection.cursor() as c:
            c.execute('SET session_replication_role = replica')
            ret = func(*args, **kwargs)
            c.execute('SET session_replication_role = DEFAULT')
        return ret
    return _inner
