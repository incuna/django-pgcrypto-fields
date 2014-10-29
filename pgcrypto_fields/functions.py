class FunctionMixin:
    """SQL cryptographic mixin."""

    def sql_function(self, function, arguments):
        """
        Generate a SQL function string.

        `function` is a pgcrypto function.

        `arguments` are arguments to pass to a function
        """
        return '{}({})'.format(function, arguments)

    def sql_encrypt_function(self, arguments):
        """Generate SQL function string for encryption."""
        return self.sql_function(self.encrypt_function, arguments)

    def sql_decrypt_function(self, arguments):
        """Generate SQL function string for decryption."""
        return self.sql_function(self.decrypt_function, arguments)


class Digest(FunctionMixin):
    """Encrypt/decrypt a binary hash based on encryption method.

    `encrypt_function` and `decrypt_function` are pgcrypto cryprographic
    functions.

    `arguments` is passed to the 'digest' function.
    """
    encrypt_function = decrypt_function = 'digest'
    arguments = "{}, '{}'"

    def sql_encrypt_function(self, value, encryption):
        """
        Return a 'digest' function to encrypt a value.

        `value` is the value to encrypt.

        `encryption` is the encryption type.
        """
        arguments = self.arguments.format(value, encryption)
        return super().sql_encrypt_function(arguments)

    def sql_decrypt_function(self, field, encryption):
        """
        Return a 'digest' function to decrypt a value.

        `field` is the field/column to decrypt.

        `encryption` is the encryption type.
        """
        arguments = self.arguments.format(field, encryption)
        return super().sql_decrypt_function(arguments)


class HMAC(FunctionMixin):
    """Encrypt/decrypt a hashed MAC with key and encryption.

    `encrypt_function` and `decrypt_function` are pgcrypto cryprographic
    functions.

    `arguments` is passed to the 'hmac' function.
    """
    encrypt_function = decrypt_function = 'hmac'
    arguments = "{}, '{}', '{}'"

    def sql_encrypt_function(self, field, password, encryption):
        """
        Return a 'hmac' function to encrypt a value.

        `value` is the value to encrypt.

        `password` is the key to encrypt/decrypt the `value`.

        `encryption` is the encryption type.
        """
        arguments = self.arguments.format(field, password, encryption)
        return super().sql_encrypt_function(arguments)

    def sql_decrypt_function(self, field, password, encryption):
        """
        Return a 'hmac' function to decrypt a value.

        `field` is the field/column to decrypt.

        `password` is the key to encrypt/decrypt the `value`.

        `encryption` is the encryption type.
        """
        arguments = self.arguments.format(field, password, encryption)
        return super().sql_decrypt_function(arguments)


class PGPPub(FunctionMixin):
    """Encrypt/Decrypt data with a public-key.

    `encrypt_function` and `decrypt_function` are pgcrypto cryprographic
    functions.

    `arguments` is passed to the function.
    """
    encrypt_function = 'pgp_pub_encrypt'
    decrypt_function = 'pgp_pub_decrypt'
    arguments = "{}, dearmor('{}')"

    def sql_encrypt_function(self, value, public_key):
        """
        Return a public key based function to encrypt a value.

        `value` is the data to encrypt.

        `public_key` is a PGP key to encrypt the `value`.
        """
        arguments = self.arguments.format(value, public_key)
        return super().sql_encrypt_function(arguments)

    def sql_decrypt_function(self, field, private_key):
        """
        Return a public key based function to decrypt a value.

        `field` is the field/column to decrypt.

        `private_key` is PGP private key to decrypt the `field`'s value'.
        """
        arguments = self.arguments.format(field, private_key)
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

    def sql_encrypt_function(self, value, key):
        """
        Return a symmetric key based function to encrypt a value.

        `value` is the data to encrypt.

        `key` is the key to encrypt/decrypt the `value`.
        """
        arguments = self.arguments.format(value, key)
        return super().sql_encrypt_function(arguments)

    def sql_decrypt_function(self, field, key):
        """
        Return a symmetric key based function to decrypt a field.

        `field` is the field/column name to decrypt.

        `key` is the key to encrypt/decrypt the `value`.
        """
        arguments = self.arguments.format(field, key)
        return super().sql_decrypt_function(arguments)
