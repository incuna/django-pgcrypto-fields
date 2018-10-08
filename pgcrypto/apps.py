from django.apps import AppConfig


class PgcryptoConfig(AppConfig):
    name = 'pgcrypto'

    def ready(self):
        """Ready for pgcrypto."""
        pass
