class TestRouter(object):

    def db_for_read(self, model, **hints):
        """Read from diff_keys."""
        if model._meta.app_label == 'diff_keys':
            return 'diff_keys'
        if model._meta.app_label == 'password_protected':
            return 'password_protected'
        return 'default'

    def db_for_write(self, model, **hints):
        """Write to diff_keys."""
        if model._meta.app_label == 'diff_keys':
            return 'diff_keys'
        if model._meta.app_label == 'password_protected':
            return 'password_protected'
        return 'default'
