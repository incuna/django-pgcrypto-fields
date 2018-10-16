class TestRouter(object):

    def db_for_read(self, model, **hints):
        """Read from diff_keys."""
        if model._meta.app_label == 'diff_keys':
            return 'diff_keys'
        return None

    def db_for_write(self, model, **hints):
        """Write to diff_keys."""
        if model._meta.app_label == 'diff_keys':
            return 'diff_keys'
        return None
