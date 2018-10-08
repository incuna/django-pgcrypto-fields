from django.apps import AppConfig


class PgcryptoConfig(AppConfig):
    name = 'pgcrypto'

    def ready(self):
        print('I DID IT')
        pass