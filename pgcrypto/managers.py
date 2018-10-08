from django.db import models

from pgcrypto.mixins import PGPMixin


class PGPManager(models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    @staticmethod
    def _get_pgp_decrypt_sql(field):
        """Decrypt sql for symmetric fields using the cast sql if required."""
        name = '"{0}"."{1}"'.format(field.model._meta.db_table, field.name)
        sql = field.decrypt_sql % name
        if hasattr(field, 'cast_sql') and field.cast_sql:
            sql = field.cast_sql % sql

        return sql

    def get_queryset(self, *args, **kwargs):
        """Decryption in queryset through meta programming."""
        skip_decrypt = kwargs.pop('skip_decrypt', None)

        qs = super().get_queryset(*args, **kwargs)

        # The Django admin skips this process because it's extremely slow
        if not skip_decrypt:
            select_sql = {}
            encrypted_fields = []

            for field in self.model._meta.get_fields():
                if isinstance(field, PGPMixin):
                    select_sql[field.name] = self._get_pgp_decrypt_sql(field)
                    encrypted_fields.append(field.name)

            # Django queryset.extra() is used here to add decryption sql to query.
            qs = qs.defer(
                *encrypted_fields
            ).extra(
                select=select_sql
            )

        return qs
