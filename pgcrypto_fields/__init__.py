from django.conf import settings


DIGEST_SQL = "digest(%s, 'sha512')"
HMAC_SQL = "hmac(%s, '{}', 'sha512')".format(settings.PGCRYPTO_KEY)

PGP_PUB_ENCRYPT_SQL = "pgp_pub_encrypt(%s, dearmor('{}'))".format(
    settings.PUBLIC_PGP_KEY,
)
PGP_SYM_ENCRYPT_SQL = "pgp_sym_encrypt(%s, '{}')".format(settings.PGCRYPTO_KEY)
