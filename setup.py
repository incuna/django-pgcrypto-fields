import sys

from setuptools import find_packages, setup

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 5)

# This check and everything above must remain compatible with Python 2.7.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of django-pgcrypto-fields requires Python {}.{}, but you're trying to
install it on Python {}.{}.
This may be because you are using a version of pip that doesn't
understand the python_requires classifier. Make sure you
have pip >= 9.0 and setuptools >= 24.2, then try again:
    $ python -m pip install --upgrade pip setuptools
    $ python -m pip install django-pgcrypto-fields
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)


with open('README.md') as readme_file:
    readme = readme_file.read()


with open('CHANGELOG.md') as changelog_file:
    changelog = changelog_file.read()

version = '2.4.0'

setup(
    name='django-pgcrypto-fields',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    version=version,
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    license='BSD',
    description='Encrypted fields for Django dealing with pgcrypto postgres extension.',
    long_description=readme + '\n\n' + changelog,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Database',
        'Topic :: Security :: Cryptography',
    ],
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-pgcrypto-fields',
    test_suite='tests',
)
