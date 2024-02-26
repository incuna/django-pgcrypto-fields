import psycopg2


def create_dbs(db_config, databases):
    """Set up the databases for test."""
    connection = psycopg2.connect(**db_config)
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    for database in databases:
        cursor.execute(f"DROP DATABASE IF EXISTS {database}")
        cursor.execute(f"CREATE DATABASE {database}")
    cursor.close()
    connection.close()
