from django.db import models


class PGPManager(models.Manager):  # pragma: no cover
    use_for_related_fields = True
    use_in_migrations = True

    # Here from backwards compatibility only
