from django.test import TestCase

from pgcrypto_fields import functions


class TestDigest(TestCase):
    """Test digest SQL function."""
    function = functions.Digest()

    def test_encrypt(self):
        """Assert the encrypt SQL 'digest' function is correct."""
        expected = "digest(field, 'md5')"
        sql = self.function.sql_encrypt_function('field', 'md5')
        self.assertEqual(sql, expected)

    def test_encrypt_function(self):
        """Assert the 'digest' encrypting function is the correct one."""
        self.assertEqual(self.function.encrypt_function, 'digest')

    def test_decrypt(self):
        """Assert the decrypt SQL 'digest' function is correct."""
        expected = "digest(field, 'md5')"
        sql = self.function.sql_decrypt_function('field', 'md5')
        self.assertEqual(sql, expected)

    def test_decrypt_function(self):
        """Assert the 'digest' decrypting function is the correct one."""
        self.assertEqual(self.function.decrypt_function, 'digest')


class TestHMAC(TestCase):
    """Test hmac SQL function."""
    function = functions.HMAC()

    def test_encrypt(self):
        """Assert the encrypt SQL 'hmac' function is correct."""
        expected = "hmac(field, 'password', 'md5')"
        sql = self.function.sql_encrypt_function('field', 'password', 'md5')
        self.assertEqual(sql, expected)

    def test_encrypt_function(self):
        """Assert the 'hmac' encrypting function is the correct one."""
        self.assertEqual(self.function.encrypt_function, 'hmac')

    def test_decrypt(self):
        """Assert the decrypt SQL 'hmac' function is correct."""
        expected = "hmac(field, 'password', 'md5')"
        sql = self.function.sql_decrypt_function('field', 'password', 'md5')
        self.assertEqual(sql, expected)

    def test_decrypt_function(self):
        """Assert the 'hmac' decrypting function is the correct one."""
        self.assertEqual(self.function.decrypt_function, 'hmac')


class TestPGPPub(TestCase):
    """Test public-key SQL function."""
    function = functions.PGPPub()

    def test_encrypt(self):
        """Assert the encrypt SQL public-key based function is correct."""
        expected = "pgp_pub_encrypt(field, dearmor('publickey'))"
        sql = self.function.sql_encrypt_function('field', 'publickey')
        self.assertEqual(sql, expected)

    def test_encrypt_function(self):
        """Assert the public-key based encrypting function is the correct one."""
        self.assertEqual(self.function.encrypt_function, 'pgp_pub_encrypt')

    def test_decrypt(self):
        """Assert the decrypt SQL public-key based function is correct."""
        expected = "pgp_pub_decrypt(field, dearmor('publickey'))"
        sql = self.function.sql_decrypt_function('field', 'publickey')
        self.assertEqual(sql, expected)

    def test_decrypt_function(self):
        """Assert the public-key based decrypting function is the correct one."""
        self.assertEqual(self.function.decrypt_function, 'pgp_pub_decrypt')


class TestPGPSym(TestCase):
    """Test symmetric-key SQL function."""
    function = functions.PGPSym()

    def test_encrypt(self):
        """Assert the encrypt SQL symmetric-key based function is correct."""
        expected = "pgp_sym_encrypt(field, 'password')"
        sql = self.function.sql_encrypt_function('field', 'password')
        self.assertEqual(sql, expected)

    def test_encrypt_function(self):
        """Assert the symmetric-key based encrypting function is the correct one."""
        self.assertEqual(self.function.encrypt_function, 'pgp_sym_encrypt')

    def test_decrypt(self):
        """Assert the decrypt SQL symmetric-key based function is correct."""
        expected = "pgp_sym_decrypt(field, 'password')"
        sql = self.function.sql_decrypt_function('field', 'password')
        self.assertEqual(sql, expected)

    def test_decrypt_function(self):
        """Assert the symmetric-key based decrypting function is the correct one."""
        self.assertEqual(self.function.decrypt_function, 'pgp_sym_decrypt')
