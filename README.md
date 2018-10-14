# django-pgcrypto-fields [![Latest Release](https://img.shields.io/pypi/v/django-pgcrypto-fields.svg)](https://pypi.org/pypi/django-pgcrypto-fields/) [![Python Versions](https://img.shields.io/pypi/pyversions/django-pgcrypto-fields.svg)](https://pypi.org/pypi/django-pgcrypto-fields/) [![Build Status](https://travis-ci.org/incuna/django-pgcrypto-fields.svg?branch=master)](https://travis-ci.org/incuna/django-pgcrypto-fields?branch=master) [![Requirements Status](https://requires.io/github/incuna/django-pgcrypto-fields/requirements.svg?branch=master)](https://requires.io/github/incuna/django-pgcrypto-fields/requirements/?branch=master) [![PyUp - Python 3](https://pyup.io/repos/github/incuna/django-pgcrypto-fields/python-3-shield.svg)](https://pyup.io/repos/github/incuna/django-pgcrypto-fields/)


`django-pgcrypto-fields` is a `Django` extension which relies upon `pgcrypto` to
encrypt and decrypt data for fields.

## Requirements

 - postgres with `pgcrypto`
 - Supports Django 1.11.x to 2.1.x
 - Compatible with Python 3 only
 
 Last version of this library that supports `Django` 1.8.x, 1.9.x, 1.10.x
 was `django-pgcrypto-fields` 2.2.0.
 

## Installation

```bash
pip install django-pgcrypto-fields
```

In your Django `settings.py`, add `pgcrypto` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    'pgcrypto',
    # Other apps
)
```

## Upgrading to 2.4.0 from previous versions

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
 - `EmailPGPPublicKeyField`
 - `IntegerPGPPublicKeyField`
 - `TextPGPPublicKeyField`
 - `DatePGPPublicKeyField`
 - `DateTimePGPPublicKeyField`

Public key encryption creates a token generated with a public key to
encrypt the data and a private key to decrypt it.

Public and private keys can be set in settings with `PUBLIC_PGP_KEY` and
`PRIVATE_PGP_KEY`.

N.B. `DatePGPPublicKeyField` and `DateTimePGPPublicKeyField` only support the following lookups:

- `__exact`
- `__gt`
- `__gte`
- `__lt`
- `__lte`
- `__range`

##### Generate GPG keys.

The public key is going to encrypt the message and the private key will be
needed to decrypt the content. The following commands have been taken from the
[pgcrypto documentation](http://www.postgresql.org/docs/devel/static/pgcrypto.html)
(see Generating PGP Keys with GnuPG).

Generating a public and a private key:

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

#### Symmetric Key Encryption Fields

Supported PGP symmetric key fields are:
 - `EmailPGPSymmetricKeyField`
 - `IntegerPGPSymmetricKeyField`
 - `TextPGPSymmetricKeyField`
 - `DatePGPSymmetricKeyField`
 - `DateTimePGPSymmetricKeyField`

Encrypt and decrypt the data with `settings.PGCRYPTO_KEY` which acts like a password.

N.B. `DatePGPSymmetricKeyField` and `DateTimePGPSymmetricKeyField` only support the following lookups:

- `__exact`
- `__gt`
- `__gte`
- `__lt`
- `__lte`
- `__range`

### Django settings

In `settings.py`:
```python
import os
BASEDIR = os.path.dirname(os.path.dirname(__file__))
PUBLIC_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'public.key'))
PRIVATE_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'private.key'))


# Used by PGPPublicKeyField
PUBLIC_PGP_KEY = open(PUBLIC_PGP_KEY_PATH).read()
PRIVATE_PGP_KEY = open(PRIVATE_PGP_KEY_PATH).read()

# Used by TextHMACField and PGPSymmetricKeyField
PGCRYPTO_KEY='ultrasecret'


# And add 'pgcrypto' to `INSTALLED_APPS` to create the extension for
# pgcrypto (in a migration).
INSTALLED_APPS = (
    'pgcrypto',
    # Other installed apps
)

```

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
    
    email_pgp_sym_field = fields.EmailPGPSymmetricKeyField()
    integer_pgp_sym_field = fields.IntegerPGPSymmetricKeyField()
    pgp_sym_field = fields.TextPGPSymmetricKeyField()
    date_pgp_sym_field = fields.DatePGPSymmetricKeyField()
    datetime_pgp_sym_field = fields.DateTimePGPSymmetricKeyField()
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

#### `.distinct('encrypted_field_name')`

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
