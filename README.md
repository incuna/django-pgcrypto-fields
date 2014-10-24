# django-pgcrypto-fields [![Build Status](https://travis-ci.org/incuna/django-pgcrypto-fields.svg?branch=master)](https://travis-ci.org/incuna/django-pgcrypto-fields?branch=master)

`django-pgcrypto-fields` is a `Django` extension which relies upon pgcrypto to
encrypt and decrypt data for fields.

## Requirements

 - postgres with pgcrypto

## Installation

### pip

```bash
pip install django-pgcrypto-fields
```

### Generate GPG keys.

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

### `settings.py`

```python
BASEDIR = os.path.dirname(os.path.dirname(__file__))
PUBLIC_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'public.key'))
PRIVATE_PGP_KEY_PATH = os.path.abspath(os.path.join(BASEDIR, 'private.key'))


PUBLIC_PGP_KEY = open(PUBLIC_PGP_KEY_PATH).read()
PRIVATE_PGP_KEY = open(PRIVATE_PGP_KEY_PATH).read()

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
    value = fields.EncryptedTextField()
```

#### Encrypting

Encrypting data happens when doing an insert to the database.

Example:
```python
>>> MyModel.objects.create(value='Value to be encrypted...')
```

#### Decrypting

Decrypting data should be done using the `Decrypt` aggregate class.

Example:
```python
>>> my_model = MyModel.objects.annotate(Decrypt('value'))
>>> my_model.value__decrypt
'Value to be encrypted....'
```
