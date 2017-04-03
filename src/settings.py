import os

print(os.environ['NBA_DB_NAME'])

DATABASE = {
    'drivername': os.environ['NBA_DB_DRIVER'],
    'host': os.environ['NBA_DB_HOST'],
    'port': os.environ['NBA_DB_PORT'],
    'username': os.environ['NBA_DB_USER'],
    'password': os.environ['NBA_DB_PW'],
    'database': os.environ['NBA_DB_NAME'],
}

