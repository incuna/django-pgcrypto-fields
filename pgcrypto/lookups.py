from django.db.models.lookups import Lookup


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
