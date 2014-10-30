from django.conf import settings

from pgcrypto_fields import aggregates


class FunctionMixin:
    """SQL cryptographic mixin for django field."""

    @classmethod
    def aggregate(cls, field):
        """Return an 'Aggregate' function to decrypt the field."""
        klass = getattr(aggregates, cls.__name__)
        return klass(field)

    @classmethod
    def sql_function(cls, function, arguments):
        """
        Generate a SQL function string.

        `function` is a pgcrypto function.

        `arguments` are arguments to pass to a function
        """
        return '{}({})'.format(function, arguments)

    @classmethod
    def sql_encrypt_function(cls, arguments):
        """Generate SQL function string for encryption."""
        return cls.sql_function(cls.encrypt_function, arguments)

    @classmethod
    def sql_decrypt_function(cls, arguments):
        """Generate SQL function string for decryption.

        `%(function)s` in `sql_template` is populated by `sql_function`.
        """
        return cls.sql_function('%(function)s', arguments)


class Digest(FunctionMixin):
    """Create a binary hash based on encryption method.

    `encrypt_function` and `decrypt_function` are pgcrypto cryprographic
    functions.

    `arguments` is passed to the 'digest' function.
    """
    encrypt_function = 'digest'
    encryption = 'md5'
    arguments = "{}, '{}'"

    @classmethod
    def sql_encrypt_function(cls):
        """
        Return a 'digest' function to encrypt a value.

        `%s` is replaced with the field's value.

        `encryption` is the encryption type.
        """
        arguments = cls.arguments.format('%s', cls.encryption)
        return super().sql_encrypt_function(arguments)


class HMAC(FunctionMixin):
    """Create a hashed MAC with key and encryption.

    `encrypt_function` and `decrypt_function` are pgcrypto cryprographic
    functions.

    `arguments` is passed to the 'hmac' function.
    """
    encrypt_function = 'hmac'
    encryption = 'md5'
    arguments = "{}, '{}', '{}'"

    @classmethod
    def sql_encrypt_function(cls):
        """
        Return a 'hmac' function to encrypt a value.

        `%s` is replaced with the field's value.

        `PGCRYPTO_KEY` is the key to encrypt/decrypt the `value`.

        `encryption` is the encryption type.
        """
        arguments = cls.arguments.format(
            '%s',
            settings.PGCRYPTO_KEY,
            cls.encryption,
        )
        return super().sql_encrypt_function(arguments)


class PGPPub(FunctionMixin):
    """Encrypt/Decrypt data with a public-key.

    `encrypt_function` and `decrypt_function` are pgcrypto cryprographic
    functions.

    `arguments` is passed to the function.

    `dearmor` is used to unwrap the key from the PGP key.
    """
    encrypt_function = 'pgp_pub_encrypt'
    decrypt_function = 'pgp_pub_decrypt'
    arguments = "{}, dearmor('{}')"

    @classmethod
    def sql_encrypt_function(cls):
        """
        Return a public key based function to encrypt a value.

        `%s` is replaced with the field's value.

        `public_key` is a PGP key to encrypt a `value`.
        """
        arguments = cls.arguments.format('%s', settings.PUBLIC_PGP_KEY)
        return super().sql_encrypt_function(arguments)

    @classmethod
    def sql_decrypt_function(cls):
        """
        Return a public key based function to decrypt a value.

        `%(field)s` is replaced by django with the field's name.

        `private_key` is PGP private key to decrypt the `field`'s value'.
        """
        arguments = cls.arguments.format(
            '%(field)s',
            settings.PRIVATE_PGP_KEY,
        )
        return super().sql_decrypt_function(arguments)


class PGPSym(FunctionMixin):
    """Encrypt/Decrypt data with a symmetric-key.

    `encrypt_function` and `decrypt_function` are pgcrypto cryprographic
    functions.

    `arguments` is passed to the function.
    """
    encrypt_function = 'pgp_sym_encrypt'
    decrypt_function = 'pgp_sym_decrypt'
    arguments = "{}, '{}'"

    @classmethod
    def sql_encrypt_function(cls):
        """
        Return a symmetric key based function to encrypt a value.

        `%s` is replaced with the field's value.

        `PGCRYPTO_KEY` is the key to encrypt/decrypt the `value`.
        """
        arguments = cls.arguments.format('%s', settings.PGCRYPTO_KEY)
        return super().sql_encrypt_function(arguments)

    @classmethod
    def sql_decrypt_function(cls):
        """
        Return a symmetric key based function to decrypt a field.

        `%(field)s` is replaced by django with the field's name.

        `PGCRYPTO_KEY` is the key to encrypt/decrypt the `value`.
        """
        arguments = cls.arguments.format(
            '%(field)s',
            settings.PGCRYPTO_KEY,
        )
        return super().sql_decrypt_function(arguments)
