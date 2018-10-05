from django.conf import settings
from django.db.models.lookups import Lookup

from pgcrypto import DIGEST_SQL, HMAC_SQL

PGCRYPTO_KEY = settings.PGCRYPTO_KEY
PRIVATE_PGP_KEY = settings.PRIVATE_PGP_KEY


class HashLookupBase(Lookup):
    """Lookup to filter hashed values.

    `HashLookup` is hashing the value on the right hand side with
    the function specified in `encrypt_sql`.
    """
    lookup_name = 'hash_of'

    def as_sql(self, qn, connection):
        """Responsible for creating the lookup with the digest SQL.

        Modify the right hand side expression to compare the value passed
        to a hash.
        """
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params

        rhs = self.encrypt_sql % rhs
        return ('{}::bytea = {}'.format(lhs, rhs)), params


class DigestLookup(HashLookupBase):
    """Digest lookup producing a hash.

    `encrypt_sql` uses pgcrypto 'digest' function to create a hash based version
    of the field's value.
    """
    encrypt_sql = DIGEST_SQL


class HMACLookup(HashLookupBase):
    """HMAC lookup producing a hash.

    `encrypt_sql` uses pgcrypto 'hmac' function to create a hash based version
    the field's value.
    """
    encrypt_sql = HMAC_SQL


class DatePGPSymmetricKeyLookupBase(Lookup):
    """Base class for Date lookups."""
    lookup_name = None  # Set in subclasses
    operator = None  # Set in subclasses

    def __init__(self, lhs, rhs):
        """Implement an abstract class."""
        super(DatePGPSymmetricKeyLookupBase, self).__init__(lhs, rhs)  # pragma: no cover

    def as_sql(self, qn, connection):
        """Build SQL with decryption and casting."""
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "cast(pgp_sym_decrypt(%s, '%s') as DATE) %s %s" % (
            lhs, PGCRYPTO_KEY, self.operator, rhs
        ), params


class DatePGPSymmetricKeyGT(DatePGPSymmetricKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'gt'
    operator = '>'


class DatePGPSymmetricKeyGTE(DatePGPSymmetricKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'gte'
    operator = '>='


class DatePGPSymmetricKeyLT(DatePGPSymmetricKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'lt'
    operator = '<'


class DatePGPSymmetricKeyLTE(DatePGPSymmetricKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'lte'
    operator = '<='


class DatePGPSymmetricKeyEXACT(DatePGPSymmetricKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'exact'
    operator = '='


class DateTimePGPSymmetricKeyLookupBase(Lookup):
    """Base class for DateTime lookups."""
    lookup_name = None  # Set in subclasses
    operator = None  # Set in subclasses

    def __init__(self, lhs, rhs):
        """Implement an abstract class."""
        super(DateTimePGPSymmetricKeyLookupBase, self).__init__(
            lhs, rhs
        )  # pragma: no cover

    def as_sql(self, qn, connection):
        """Build SQL with decryption and casting."""
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "cast(pgp_sym_decrypt(%s, '%s') as TIMESTAMP) %s %s" % (
            lhs, PGCRYPTO_KEY, self.operator, rhs
        ), params


class DateTimePGPSymmetricKeyGT(DateTimePGPSymmetricKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'gt'
    operator = '>'


class DateTimePGPSymmetricKeyGTE(DateTimePGPSymmetricKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'gte'
    operator = '>='


class DateTimePGPSymmetricKeyLT(DateTimePGPSymmetricKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'lt'
    operator = '<'


class DateTimePGPSymmetricKeyLTE(DateTimePGPSymmetricKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'lte'
    operator = '<='


class DateTimePGPSymmetricKeyEXACT(DateTimePGPSymmetricKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'exact'
    operator = '='


class DatePGPPublicKeyLookupBase(Lookup):
    """Base class for Date lookups."""
    lookup_name = None  # Set in subclasses
    operator = None  # Set in subclasses

    def __init__(self, lhs, rhs):
        """Implement an abstract class."""
        super(DatePGPPublicKeyLookupBase, self).__init__(lhs, rhs)  # pragma: no cover

    def as_sql(self, qn, connection):
        """Build SQL with decryption and casting."""
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "cast(pgp_pub_decrypt(%s, dearmor('%s')) as DATE) %s %s" % (
            lhs, PRIVATE_PGP_KEY, self.operator, rhs
        ), params


class DatePGPPublicKeyGT(DatePGPPublicKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'gt'
    operator = '>'


class DatePGPPublicKeyGTE(DatePGPPublicKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'gte'
    operator = '>='


class DatePGPPublicKeyLT(DatePGPPublicKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'lt'
    operator = '<'


class DatePGPPublicKeyLTE(DatePGPPublicKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'lte'
    operator = '<='


class DatePGPPublicKeyEXACT(DatePGPPublicKeyLookupBase):
    """Lookup for Date."""
    lookup_name = 'exact'
    operator = '='


class DateTimePGPPublicKeyLookupBase(Lookup):
    """Base class for DateTime lookups."""
    lookup_name = None  # Set in subclasses
    operator = None  # Set in subclasses

    def __init__(self, lhs, rhs):
        """Implement an abstract class."""
        super(DateTimePGPPublicKeyLookupBase, self).__init__(lhs, rhs)  # pragma: no cover

    def as_sql(self, qn, connection):
        """Build SQL with decryption and casting."""
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "cast(pgp_pub_decrypt(%s, dearmor('%s')) as TIMESTAMP) %s %s" % (
            lhs, PRIVATE_PGP_KEY, self.operator, rhs
        ), params


class DateTimePGPPublicKeyGT(DateTimePGPPublicKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'gt'
    operator = '>'


class DateTimePGPPublicKeyGTE(DateTimePGPPublicKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'gte'
    operator = '>='


class DateTimePGPPublicKeyLT(DateTimePGPPublicKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'lt'
    operator = '<'


class DateTimePGPPublicKeyLTE(DateTimePGPPublicKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'lte'
    operator = '<='


class DateTimePGPPublicKeyEXACT(DateTimePGPPublicKeyLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'exact'
    operator = '='
