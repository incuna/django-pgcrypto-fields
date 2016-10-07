from setuptools import find_packages, setup


version = '1.0.1'


setup(
    name='django-pgcrypto-fields',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    version=version,
    license='BSD',
    description='Encrypted fields dealing with pgcrypto postgres extension.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Topic :: Database',
        'Topic :: Security :: Cryptography',
    ],
    author='Incuna Ltd',
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-pgcrypto-fields',
)
