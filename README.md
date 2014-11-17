# django-pgcrypto-fields [![Build Status](https://travis-ci.org/incuna/django-pgcrypto-fields.svg?branch=master)](https://travis-ci.org/incuna/django-pgcrypto-fields?branch=master) [![Requirements Status](https://requires.io/github/incuna/django-pgcrypto-fields/requirements.svg?branch=master)](https://requires.io/github/incuna/django-pgcrypto-fields/requirements/?branch=master)

`django-pgcrypto-fields` is a `Django` extension which relies upon pgcrypto to
encrypt and decrypt data for fields.

`django-pgcrypto-fields` has 4 fields grouped in two categories:
  - hash based fields (`DigestField` and `HMACField`);
  - pgp fields (`PGPPublicKeyField` and `PGPSymmetricKeyField`).


## Requirements

 - postgres with pgcrypto

## Installation

### pip

```bash
pip install django-pgcrypto-fields
```

### Fields

#### DigestField

`DigestField` is a hash based field. The value is hashed in the database when
saved with the `digest` pgcrypto function using the `sha512` algorithm.

#### HMACField

`HMACField` is a hash based field. Value is hashed in the database when
saved with the `hmac` pgcrypto function using a key and the `sha512` algorithm.

`key` is set in `settings.PGCRYPTO_KEY`.

#### PGPPublicKeyField

Public key encryption. It generates a token generated with a public key to
encrypt the data and a private key to decrypt it.

Public and private keys can be set in settings with `PUBLIC_PGP_KEY` and
`PRIVATE_PGP_KEY`.

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

#### PGPSymmetricKeyField

Symmetric key encryption. Encrypt and decrypt the data with `settings.PGCRYPTO_KEY`.

### `settings.py`

```python
BASEDIR = os.path.dirname(os.path.dirname(__file__))
PUBLIC_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'public.key'))
PRIVATE_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'private.key'))


# Used by PGPPublicKeyField
PUBLIC_PGP_KEY = open(PUBLIC_PGP_KEY_PATH).read()
PRIVATE_PGP_KEY = open(PRIVATE_PGP_KEY_PATH).read()

# Used by HMACField and PGPSymmetricKeyField
PGCRYPTO_KEY='ultrasecret'


# And add 'pgcrypto_fields' to `INSTALLED_APPS` to create the extension for
# pgcrypto (in a migration).
INSTALLED_APPS = (
    ...
    'pgcrypto_fields',
    ...
)

```

### Usage

#### Model definition

```python
from django.db import models

from pgcrypto_fields import fields

class MyModel(models.Model):
    digest_field = fields.DigestField()
    hmac_field = fields.HMACField()

    pgp_pub_field = fields.PGPPublicKeyField()
    pgp_sym_field = fields.PGPSymmetricKeyField()
```

#### Encrypting

Data is encrypted when inserted into the database.

Example:
```python
>>> MyModel.objects.create(value='Value to be encrypted...')
```

#### Decrypting

Data is decrypted when using the `Decrypt` aggregate class.

Example:
```python
>>> from pgcrypto_fields.aggregates import Decrypt
>>> my_model = MyModel.objects.annotate(Decrypt('value')).get()
>>> my_model.value__decrypt
'Value decrypted'
```
