DIGEST_SQL = "digest(%s, 'sha512')"
HMAC_SQL = "hmac(%s, '{}', 'sha512')"

PGP_PUB_ENCRYPT_SQL_WITH_NULLIF = "pgp_pub_encrypt(nullif(%s, NULL)::text, dearmor('{}'))"
PGP_SYM_ENCRYPT_SQL_WITH_NULLIF = "pgp_sym_encrypt(nullif(%s, NULL)::text, '{}')"

PGP_PUB_ENCRYPT_SQL = "pgp_pub_encrypt(%s, dearmor('{}'))"
PGP_SYM_ENCRYPT_SQL = "pgp_sym_encrypt(%s, '{}')"

PGP_PUB_DECRYPT_SQL = "pgp_pub_decrypt(%s, dearmor('{}'))::%s"
PGP_SYM_DECRYPT_SQL = "pgp_sym_decrypt(%s, '{}')::%s"
