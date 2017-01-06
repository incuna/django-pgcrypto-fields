from django.conf import settings
from django.db import models


class PGPManager(models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    @staticmethod
    def _get_pgp_symmetric_decrypt_sql(field):
        """Decrypt sql for symmetric fields using the cast sql if required."""
        sql = """pgp_sym_decrypt("{0}"."{1}", '{2}')"""
        if hasattr(field, 'cast_sql'):
            sql = field.cast_sql % sql

        return sql.format(
            field.model._meta.db_table,
            field.name,
            settings.PGCRYPTO_KEY,
        )

    @staticmethod
    def _get_pgp_public_key_decrypt_sql(field):
        """Decrypt sql for public key fields using the cast sql if required."""
        sql = """pgp_pub_decrypt("{0}"."{1}", dearmor('{2}'))"""

        if hasattr(field, 'cast_sql'):
            sql = field.cast_sql % sql

        return sql.format(
            field.model._meta.db_table,
            field.name,
            settings.PRIVATE_PGP_KEY,
        )

    def get_queryset(self, *args, **kwargs):
        """Decryption in queryset through meta programming."""
        # importing here otherwise there's a circular reference issue
        from pgcrypto.mixins import PGPSymmetricKeyFieldMixin, PGPPublicKeyFieldMixin

        skip_decrypt = kwargs.pop('skip_decrypt', None)

        qs = super().get_queryset(*args, **kwargs)

        # The Django admin skips this process because it's extremely slow
        if not skip_decrypt:
            select_sql = {}
            encrypted_fields = []

            for field in self.model._meta.get_fields():
                if isinstance(field, PGPSymmetricKeyFieldMixin):
                    select_sql[field.name] = self._get_pgp_symmetric_decrypt_sql(field)
                    encrypted_fields.append(field.name)
                elif isinstance(field, PGPPublicKeyFieldMixin):
                    select_sql[field.name] = self._get_pgp_public_key_decrypt_sql(field)
                    encrypted_fields.append(field.name)

            # Django queryset.extra() is used here to add decryption sql to query.
            qs = qs.defer(
                *encrypted_fields
            ).extra(
                select=select_sql
            )

        return qs
