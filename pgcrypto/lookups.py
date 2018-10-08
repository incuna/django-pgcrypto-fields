from django.db.models.lookups import FieldGetDbPrepValueIterableMixin, Lookup


class HashLookup(Lookup):
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
        rhs = self.lhs.field.encrypt_sql % rhs
        return ('{}::bytea = {}'.format(lhs, rhs)), params


class DateTimeLookupBase(Lookup):
    """Base class for Date or DateTime lookups."""
    lookup_name = None  # Set in subclasses
    operator = None  # Set in subclasses
    cast = None  # Set in subclasses

    def as_sql(self, qn, connection):
        """Build SQL with decryption and casting."""
        lhs, params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params.extend(rhs_params)
        rhs = self.get_rhs_op(connection, rhs)
        return "%s %s" % (lhs, rhs), params

    def get_rhs_op(self, connection, rhs):
        """Build right hand SQL with operator."""
        return "%s %s" % (self.operator, rhs)


class DateTimeGtLookup(DateTimeLookupBase):
    """Lookup for Date or DateTime."""
    lookup_name = 'gt'
    operator = '>'


class DateTimeGteLookup(DateTimeLookupBase):
    """Lookup for Date or DateTime."""
    lookup_name = 'gte'
    operator = '>='


class DateTimeLtLookup(DateTimeLookupBase):
    """Lookup for Date or DateTime."""
    lookup_name = 'lt'
    operator = '<'


class DateTimeLteLookup(DateTimeLookupBase):
    """Lookup for Date or DateTime."""
    lookup_name = 'lte'
    operator = '<='


class DateTimeExactLookup(DateTimeLookupBase):
    """Lookup for Date or DateTime."""
    lookup_name = 'exact'
    operator = '='


class DateTimeRangeLookup(FieldGetDbPrepValueIterableMixin, DateTimeLookupBase):
    """Lookup for Date or DateTime."""
    lookup_name = 'range'
    operator = 'BETWEEN'

    def get_rhs_op(self, connection, rhs):
        """Build right hand sql with operator."""
        return "%s %s AND %s" % (self.operator, rhs[0], rhs[1])
