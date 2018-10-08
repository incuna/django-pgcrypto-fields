from django.conf import settings


CAST_TO_TEXT = "nullif(%s, NULL)::text"
DIGEST_SQL = "digest(%s, 'sha512')"
HMAC_SQL = "hmac(%s, '{}', 'sha512')".format(settings.PGCRYPTO_KEY)

INTEGER_PGP_PUB_ENCRYPT_SQL = "pgp_pub_encrypt({}, dearmor('{}'))".format(
    CAST_TO_TEXT,
    settings.PUBLIC_PGP_KEY,
)
INTEGER_PGP_SYM_ENCRYPT_SQL = "pgp_sym_encrypt({}, '{}')".format(
    CAST_TO_TEXT,
    settings.PGCRYPTO_KEY,
)

PGP_PUB_ENCRYPT_SQL = "pgp_pub_encrypt(%s, dearmor('{}'))".format(
    settings.PUBLIC_PGP_KEY,
)
PGP_PUB_DECRYPT_SQL = "pgp_pub_decrypt(%s, dearmor('{}'))::%s".format(
    settings.PRIVATE_PGP_KEY,
)
PGP_SYM_ENCRYPT_SQL = "pgp_sym_encrypt(%s, '{}')".format(settings.PGCRYPTO_KEY)
PGP_SYM_DECRYPT_SQL = "pgp_sym_decrypt(%s, '{}')::%s".format(settings.PGCRYPTO_KEY)
