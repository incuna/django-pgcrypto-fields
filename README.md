# django-pgcrypto-fields

[![Latest Release](https://img.shields.io/pypi/v/django-pgcrypto-fields.svg)](https://pypi.org/pypi/django-pgcrypto-fields/) [![Python Versions](https://img.shields.io/pypi/pyversions/django-pgcrypto-fields.svg)](https://pypi.org/pypi/django-pgcrypto-fields/) [![Build Status](https://travis-ci.org/incuna/django-pgcrypto-fields.svg?branch=master)](https://travis-ci.org/incuna/django-pgcrypto-fields?branch=master) [![Requirements Status](https://requires.io/github/incuna/django-pgcrypto-fields/requirements.svg?branch=master)](https://requires.io/github/incuna/django-pgcrypto-fields/requirements/?branch=master) [![Updates](https://pyup.io/repos/github/incuna/django-pgcrypto-fields/shield.svg)](https://pyup.io/repos/github/incuna/django-pgcrypto-fields/) [![Coverage Status](https://coveralls.io/repos/github/incuna/django-pgcrypto-fields/badge.svg?branch=master)](https://coveralls.io/github/incuna/django-pgcrypto-fields?branch=master)

`django-pgcrypto-fields` is a `Django` extension which relies upon `pgcrypto` to
encrypt and decrypt data for fields.

## Requirements

 - postgres with `pgcrypto`
 - Supports Django 2.2.x, 3.0.x, 3.1.x and 3.2.x
 - Compatible with Python 3 only
 
 Last version of this library that supports `Django` 1.8.x, 1.9.x, 1.10.x
 was `django-pgcrypto-fields` 2.2.0.
 
 Last version of this library that supports `Django` 2.0.x and 2.1.x was
 was `django-pgcrypto-fields` 2.5.2.
 

## Installation

### Install package 

```bash
pip install django-pgcrypto-fields
```

### Django settings

Our library support different crypto keys for multiple databases by 
defining the keys in your `DATABASES` settings.

In `settings.py`:
```python
import os
BASEDIR = os.path.dirname(os.path.dirname(__file__))
PUBLIC_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'public.key'))
PRIVATE_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'private.key'))

# Used by PGPPublicKeyField used by default if not specified by the db
PUBLIC_PGP_KEY = open(PUBLIC_PGP_KEY_PATH).read()
PRIVATE_PGP_KEY = open(PRIVATE_PGP_KEY_PATH).read()

# Used by TextHMACField and PGPSymmetricKeyField if not specified by the db
PGCRYPTO_KEY='ultrasecret'

DIFF_PUBLIC_PGP_KEY_PATH = os.path.abspath(
    os.path.join(BASEDIR, 'tests/keys/public_diff.key')
)
DIFF_PRIVATE_PGP_KEY_PATH = os.path.abspath(
    os.path.join(BASEDIR, 'tests/keys/private_diff.key')
)

# And add 'pgcrypto' to `INSTALLED_APPS` to create the extension for
# pgcrypto (in a migration).
INSTALLED_APPS = (
    'pgcrypto',
    # Other installed apps
)

DATABASES = {
    # This db will use the default keys above
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pgcryto_fields',
        'USER': 'pgcryto_fields',
        'PASSWORD': 'xxxx',
        'HOST': 'psql.test.com',
        'PORT': 5432,
        'OPTIONS': {
            'sslmode': 'require',
        }
    },
    'diff_keys': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pgcryto_fields_diff',
        'USER': 'pgcryto_fields_diff',
        'PASSWORD': 'xxxx',
        'HOST': 'psqldiff.test.com',
        'PORT': 5432,
        'OPTIONS': {
            'sslmode': 'require',
        },
        'PGCRYPTO_KEY': 'djangorocks',
        'PUBLIC_PGP_KEY': open(DIFF_PUBLIC_PGP_KEY_PATH, 'r').read(),
        'PRIVATE_PGP_KEY': open(DIFF_PRIVATE_PGP_KEY_PATH, 'r').read(),
    },
}
```

### Generate GPG keys if using Public Key Encryption

The public key is going to encrypt the message and the private key will be
needed to decrypt the content. The following commands have been taken from the
[pgcrypto documentation](http://www.postgresql.org/docs/devel/static/pgcrypto.html)
(see Generating PGP Keys with GnuPG).

Generating a public and a private key (The preferred key type is "DSA and Elgamal".):

```bash
$ gpg --gen-key
$ gpg --list-secret-keys

/home/bob/.gnupg/secring.gpg
---------------------------
sec   2048R/21 2014-10-23
uid                  Test Key <example@example.com>
ssb   2048R/42 2014-10-23


$ gpg -a --export 42 > public.key
$ gpg -a --export-secret-keys 21 > private.key
```

#### Limitations

This library currently does not support Public Key Encryption private keys that are password protected yet. See Issue #89 to help implement it.

### Upgrading to 2.4.0 from previous versions

The 2.4.0 version of this library received a large rewrite in order to support 
auto-decryption when getting encrypted field data as well as the ability to filter 
on encrypted fields without using the old PGPCrypto aggregate functions available
in previous versions.

The following items in this library have been removed and therefore references in 
your application to these items need to be removed as well:

* `managers.PGPManager`
* `admin.PGPAdmin`
* `aggregates.*`

## Fields

`django-pgcrypto-fields` has 3 kinds of fields:
  - Hash based fields
  - Public Key (PGP) fields
  - Symmetric fields

#### Hash Based Fields

Supported hash based fields are:
 - `TextDigestField`
 - `TextHMACField`

`TextDigestField` is hashed in the database using the `digest` pgcrypto function 
using the `sha512` algorithm.

`TextHMACField` is hashed in the database using the `hmac` pgcrypto function 
using a key and the `sha512` algorithm. This is similar to the digest version however
the hash can only be recalculated knowing the key. This prevents someone from altering 
the data and also changing the hash to match.

#### Public Key Encryption Fields

Supported PGP public key fields are:
 - `CharPGPPublicKeyField`
 - `EmailPGPPublicKeyField`
 - `TextPGPPublicKeyField`
 - `DatePGPPublicKeyField`
 - `DateTimePGPPublicKeyField`
 - `TimePGPPublicKeyField`
 - `IntegerPGPPublicKeyField`
 - `BigIntegerPGPPublicKeyField`
 - `DecimalPGPPublicKeyField`
 - `FloatPGPPublicKeyField`
 - `BooleanPGPPublicKeyField`

Public key encryption creates a token generated with a public key to
encrypt the data and a private key to decrypt it.

Public and private keys can be set in settings with `PUBLIC_PGP_KEY` and
`PRIVATE_PGP_KEY`.

#### Symmetric Key Encryption Fields

Supported PGP symmetric key fields are:
 - `CharPGPSymmetricKeyField`
 - `EmailPGPSymmetricKeyField`
 - `TextPGPSymmetricKeyField`
 - `DatePGPSymmetricKeyField`
 - `DateTimePGPSymmetricKeyField`
 - `TimePGPSymmetricKeyField`
 - `IntegerPGPSymmetricKeyField`
 - `BigIntegerPGPSymerticKeyField`
 - `DecimalPGPSymmetricKeyField`
 - `FloatPGPSymmetricKeyField`
 - `BooleanPGPSymmetricKeyField`


Encrypt and decrypt the data with `settings.PGCRYPTO_KEY` which acts like a password.

### Django Model Field Equivalents 

| Django Field    | Public Key Field            | Symmetric Key Field            |
|-----------------|-----------------------------|--------------------------------|
| `CharField`     | `CharPGPPublicKeyField`     | `CharPGPSymmetricKeyField`     |
| `EmailField`    | `EmailPGPPublicKeyField`    | `EmailPGPSymmetricKeyField`    |
| `TextField`     | `TextPGPPublicKeyField`     | `TextPGPSymmetricKeyField`     |
| `DateField`     | `DatePGPPublicKeyField`     | `DatePGPSymmetricKeyField`     |
| `DateTimeField` | `DateTimePGPPublicKeyField` | `DateTimePGPSymmetricKeyField` |
| `TimeField`     | `TimePGPPublicKeyField`     | `TimePGPSymmetricKeyField`     |
| `IntegerField`  | `IntegerPGPPublicKeyField`  | `IntegerPGPSymmetricKeyField`  |
| `BigIntegerField`  | `BigIntegerPGPPublicKeyField`  | `BigIntegerPGPSymmetricKeyField`  |
| `DecimalField`  | `DecimalPGPPublicKeyField`  | `DecimalPGPSymmetricKeyField`  |
| `FloatField`    | `FloatPGPPublicKeyField`    | `FloatPGPSymmetricKeyField`    |
| `BooleanField`  | `BooleanPGPPublicKeyField`  | `BooleanPGPSymmetricKeyField`  |

**Other Django model fields are not currently supported. Pull requests are welcomed.**

### Usage

#### Model Definition

```python
from django.db import models

from pgcrypto import fields

class MyModel(models.Model):
    digest_field = fields.TextDigestField()
    digest_with_original_field = fields.TextDigestField(original='pgp_sym_field')
    hmac_field = fields.TextHMACField()
    hmac_with_original_field = fields.TextHMACField(original='pgp_sym_field')

    email_pgp_pub_field = fields.EmailPGPPublicKeyField()
    integer_pgp_pub_field = fields.IntegerPGPPublicKeyField()
    pgp_pub_field = fields.TextPGPPublicKeyField()
    date_pgp_pub_field = fields.DatePGPPublicKeyField()
    datetime_pgp_pub_field = fields.DateTimePGPPublicKeyField()
    time_pgp_pub_field = fields.TimePGPPublicKeyField()
    decimal_pgp_pub_field = fields.DecimalPGPPublicKeyField()
    float_pgp_pub_field = fields.FloatPGPPublicKeyField()
    boolean_pgp_pub_field = fields.BooleanPGPPublicKeyField()
    
    email_pgp_sym_field = fields.EmailPGPSymmetricKeyField()
    integer_pgp_sym_field = fields.IntegerPGPSymmetricKeyField()
    pgp_sym_field = fields.TextPGPSymmetricKeyField()
    date_pgp_sym_field = fields.DatePGPSymmetricKeyField()
    datetime_pgp_sym_field = fields.DateTimePGPSymmetricKeyField()
    time_pgp_sym_field = fields.TimePGPSymmetricKeyField()
    decimal_pgp_sym_field = fields.DecimalPGPSymmetricKeyField()
    float_pgp_sym_field = fields.FloatPGPSymmetricKeyField()
    boolean_pgp_sym_field = fields.BooleanPGPSymmetricKeyField()
```

#### Encrypting

Data is automatically encrypted when inserted into the database.

Example:
```
>>> MyModel.objects.create(value='Value to be encrypted...')
```

Hash fields can have hashes auto updated if you use the `original` attribute. This
attribute allows you to indicate another field name to base the hash value on.

```python
from django.db import models

from pgcrypto import fields

class User(models.Model):
    first_name = fields.TextPGPSymmetricKeyField(max_length=20, verbose_name='First Name')
    first_name_hashed = fields.TextHMACField(original='first_name') 
```

In the above example, if you specify the optional original attribute it would 
take the unencrypted value from the first_name model field as the input value 
to create the hash. If you did not specify an original attribute, the field 
would work as it does now and would remain backwards compatible.

##### PGP fields

When accessing the field name attribute on a model instance we are getting the
decrypted value.

Example:
```
>>> # When using a PGP public key based encryption
>>> my_model = MyModel.objects.get()
>>> my_model.value
'Value decrypted'
```

Filtering encrypted values is now handled automatically as of 2.4.0. And `aggregate`
methods are not longer supported and have been removed from the library.

Also, auto-decryption is support for `select_related()` models.

```python
from django.db import models

from pgcrypto import fields


class EncryptedFKModel(models.Model):
    fk_pgp_sym_field = fields.TextPGPSymmetricKeyField(blank=True, null=True)


class EncryptedModel(models.Model):
    pgp_sym_field = fields.TextPGPSymmetricKeyField(blank=True, null=True)
    fk_model = models.ForeignKey(
        EncryptedFKModel, blank=True, null=True, on_delete=models.CASCADE
    )
```

Example:
```
>>> import EncryptedModel
>>> my_model = EncryptedModel.objects.get().select_releated('fk_model')
>>> my_model.pgp_sym_field
'Value decrypted'
>>> my_model.fk_model.fk_pgp_sym_field
'Value decrypted'
```

##### Hash fields

To filter hash based values we need to compare hashes. This is achieved by using
a `__hash_of` lookup.

Example:
```
>>> my_model = MyModel.objects.filter(digest_field__hash_of='value')
[<MyModel: MyModel object>]
>>> my_model = MyModel.objects.filter(hmac_field__hash_of='value')
[<MyModel: MyModel object>]

```

## Limitations

### Unique Indexes

It is usually not possible to index a `bytea` column in the database as the value in the index exceeds the the pgsql's maximum length allowed for an index (8192 bytes). One solution is to create a digest message of the value that you want unique and apply the unique constraint to the digest.

You can use the hash field ability to auto-create digest on the value of another field in the same model using the `original` argument. In the example below, a digest is created for unencrypted value that is in the `name` field when the model is saved or updated. A unique constraint exists on the name_digest so no two digests are allowed.  Note well that bulk updates do NOT cause hashes to be updated.

```python
from django.db import models
from pgcrypto import fields

class Product(models.Model):
    name_digest = fields.TextDigestField(original='name')
    name = fields.TextPGPSymmetricKeyField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name_digest', ],
                name='name_digest_unique'
            )
       ]
```

### `.distinct('encrypted_field_name')`

Due to a missing feature in the Django ORM, using `distinct()` on an encrypted field
does not work for Django 2.0.x and lower.

The normal distinct works on Django 2.1.x and higher:

```python
items = EncryptedFKModel.objects.filter(
    pgp_sym_field__startswith='P'
).only(
    'id', 'pgp_sym_field', 'fk_model__fk_pgp_sym_field'
).distinct(
    'pgp_sym_field'
)
```

Workaround for Django 2.0.x and lower:

```python
from django.db import models

items = EncryptedFKModel.objects.filter(
    pgp_sym_field__startswith='P'
).annotate(
    _distinct=models.F('pgp_sym_field')
).only(
    'id', 'pgp_sym_field', 'fk_model__fk_pgp_sym_field'
).distinct(
    '_distinct'
)
```

This works because the annotated field is auto-decrypted by Django as a `F` field and that 
field is used in the `distinct()`.

### Migrating existing fields into PGCrypto Fields

Migrating existing fields into PGCrypto Fields is not performed by this library.  You will need to migrate the data 
in a forwards migration or other means. The only migration that is supported except to create/activate the pgcrypto 
extension in Postgres.

Migrating data is complicated as there might be a few things to consider such as:

* the shape of the data
* validations/constrains done on the table/model/form and anywhere else

The library has no way of doing all these guesses or to make all these decisions.

If you need to migrate data from unencrypted fields to encrypted fields, three ways to solve it:

1. When there's no data in the db it should be possible to start from scratch by recreating the db
1. When there's no data in the table it should be possible to recreate the table
1. When there's data or if the project is shared it should be possible to do it in a non destructive way

**Option 1: No data is in the db**

1. Drop the database
1. Squash the migrations
1. Recreate the db

**Option 2: No data in the table**

1. Create a migration to drop the table
1. Create a new migration for the table with the encrypted field
1. Optionally squash the migration

**Option 3: Migrating in a non-destructive way**

The goal here is to be able to use to legacy field if something goes wrong.

Part 1:

1. Create new field
1. When data is saved write both to legacy and new field
1. Create a data migration to cast data from legacy field to new field
1. check existing data from legacy and new field are the same if possible

Part 2:

1. Rename the fields and drop legacy fields
1. Update the code to use only the new field

## Common Errors

### `psycopg2.errors.UndefinedFunction: function pgp_sym_encrypt(numeric, unknown) does not exist`

This commonly means you do not have the `pgcrypto` extension installed in Postgres.  Run the migration available in this library or install it manually in pgsql console.


## Security Limitations

Taken direction from the PostgreSQL documentation:

https://www.postgresql.org/docs/9.6/static/pgcrypto.html#AEN187024

All pgcrypto functions run inside the database server. That means that all the 
data and passwords move between pgcrypto and client applications in clear text. Thus you must:

1. Connect locally or use SSL connections.
1. Trust both system and database administrator.

If you cannot, then better do crypto inside client application.

The implementation does not resist side-channel attacks. For example, the time 
required for a pgcrypto decryption function to complete varies among ciphertexts of 
a given size.
