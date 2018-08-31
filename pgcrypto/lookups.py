from django.conf import settings
from django.db.models.lookups import Lookup

from pgcrypto import DIGEST_SQL, HMAC_SQL

PGCRYPTO_KEY = settings.PGCRYPTO_KEY


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


class DateLookupBase(Lookup):
    """Base class for Date lookups."""
    lookup_name = None  # Set in subclasses
    operator = None  # Set in subclasses

    def __init__(self, lhs, rhs):
        """Implement an abstract class."""
        super(DateLookupBase, self).__init__(lhs, rhs)  # pragma: no cover

    def as_sql(self, qn, connection):
        """Build SQL with decryption and casting."""
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "cast(pgp_sym_decrypt(%s, '%s') as DATE) %s %s" % (
            lhs, PGCRYPTO_KEY, self.operator, rhs
        ), params


class DateGT(DateLookupBase):
    """Lookup for Date."""
    lookup_name = 'gt'
    operator = '>'


class DateGTE(DateLookupBase):
    """Lookup for Date."""
    lookup_name = 'gte'
    operator = '>='


class DateLT(DateLookupBase):
    """Lookup for Date."""
    lookup_name = 'lt'
    operator = '<'


class DateLTE(DateLookupBase):
    """Lookup for Date."""
    lookup_name = 'lte'
    operator = '<='


class DateEXACT(DateLookupBase):
    """Lookup for Date."""
    lookup_name = 'exact'
    operator = '='


class DateTimeLookupBase(Lookup):
    """Base class for DateTime lookups."""
    lookup_name = None  # Set in subclasses
    operator = None  # Set in subclasses

    def as_sql(self, qn, connection):
        """Build SQL with decryption and casting."""
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "cast(pgp_sym_decrypt(%s, '%s') as TIMESTAMP) %s %s" % (
            lhs, PGCRYPTO_KEY, self.operator, rhs
        ), params


class DateTimeGT(DateTimeLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'gt'
    operator = '>'


class DateTimeGTE(DateTimeLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'gte'
    operator = '>='


class DateTimeLT(DateTimeLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'lt'
    operator = '<'


class DateTimeLTE(DateTimeLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'lte'
    operator = '<='


class DateTimeEXACT(DateTimeLookupBase):
    """Lookup for DateTime."""
    lookup_name = 'exact'
    operator = '='
