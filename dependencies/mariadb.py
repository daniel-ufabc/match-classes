import sys
import time
import config
import pymysql

conn = None
while not conn:
    try:
        conn = pymysql.connect(
            host=config.DATABASE_HOST,
            port=config.DATABASE_PORT,
            user=config.DATABASE_USER,
            db=config.DATABASE_NAME,
            password=config.DATABASE_PASSWORD,
        )
    except pymysql.err.OperationalError as e:
        if int(e.args[0]) == 1049:
            # Unknown database...
            print(f'Database {config.DATABASE_NAME} does not exist.')
            sys.exit(1)
        elif int(e.args[0]) == 1044:
            # Access denied...
            print(f'User {config.DATABASE_USER} does not have access to database {config.DATABASE_NAME}.')
            sys.exit(1)

        time.sleep(2)

conn.close()
del conn
# Now, MariaDB server is up and running...


import storage

db = storage.Database()
