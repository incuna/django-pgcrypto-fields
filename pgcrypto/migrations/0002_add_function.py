from django.db import migrations

FUNCTION_SQL = "
CREATE OR REPLACE FUNCTION pgp_sym_decrypt_null_on_err(data bytea, psw text) RETURNS text AS $$
BEGIN
  RETURN pgp_sym_decrypt(data, psw);
EXCEPTION
  WHEN external_routine_invocation_exception THEN
    RAISE DEBUG USING
       MESSAGE = format('Decryption failed: SQLSTATE %s, Msg: %s',
                        SQLSTATE,SQLERRM),
       HINT = 'pgp_sym_encrypt(...) failed; check your key',
       ERRCODE = 'external_routine_invocation_exception';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;"

class Migration(migrations.Migration):

    dependencies = [
        ('pgcrypto', '0001_add_pgcrypto_extension'),
    ]

    operations = [
        migrations.RunSQL(FUNCTION_SQL)
    ]

