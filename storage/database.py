from pymysqlpool.pool import Pool
import pymysql
from pymysql.err import InternalError, OperationalError
from contextlib import contextmanager
import coloredlogs
import logging

import config

coloredlogs.install()
logging.info("Starting log...")


def query(connection, query_string, args=None):
    # logging.debug('QUERY:')
    # logging.warning(query_string)
    # logging.error(args)
    with connection.cursor() as cursor:
        n = cursor.execute(query_string, args)
        response = cursor.fetchall()
    return n, response


def query_many(connection, query_string, args_seq):
    # logging.debug('QUERY MANY:')
    # logging.warning(query_string)
    # logging.error(args_seq)
    with connection.cursor() as cursor:
        n = cursor.executemany(query_string, args_seq)
        response = cursor.fetchall()
    return n, response


class Database:
    def __init__(self, pooling=True,
                 db_host=config.DATABASE_HOST,
                 db_port=config.DATABASE_PORT,
                 db_user=config.DATABASE_USER,
                 db_password=config.DATABASE_PASSWORD,
                 autocommit=False,
                 db_name=config.DATABASE_NAME,
                 cursor_class=pymysql.cursors.Cursor):
        self.last_n = None
        self.pool = None
        self.conn = None
        self.host = db_host
        self.port = db_port
        self.user = db_user
        self.password = db_password
        self.dbname = db_name
        self.pooling = pooling
        self.autocommit = autocommit
        self.cursor_class = cursor_class
        if pooling:
            self._init_pool()
        else:
            self._init_connection()

    def __del__(self):
        if not self.pooling and self.conn:
            self.conn.close()

    def _init_connection(self):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.dbname,
            charset=config.DATABASE_CHARSET,
            cursorclass=self.cursor_class,
            autocommit=self.autocommit
        )

    def _init_pool(self):
        self.pool = Pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.dbname,
            charset=config.DATABASE_CHARSET,
            cursorclass=self.cursor_class,
            autocommit=self.autocommit,
            max_size=config.DATABASE_CONNECTION_POOL_SIZE
        )

    @contextmanager
    def connection(self, ping=False, do_not_begin=False, begin=False):
        if not self.pooling:
            if ping:
                self.conn.ping(reconnect=True)
            if begin or not do_not_begin and not self.autocommit:
                self.conn.begin()
            yield self.conn
            if begin or not do_not_begin and not self.autocommit:
                self.conn.commit()
        else:
            connection = self.pool.get_conn()
            try:
                self.conn = connection
                if ping:
                    self.conn.ping(reconnect=True)
                if begin or not do_not_begin and not self.autocommit:
                    connection.begin()
                yield connection
                if begin or not do_not_begin and not self.autocommit:
                    connection.commit()
                self.conn = None
            finally:
                self.pool.release(connection)

    def _query(self, sql, args, query_func):
        with self.connection(ping=True) as connection:
            try:
                return query_func(connection, sql, args)
            except (InternalError, OperationalError) as e:
                code, _ = e.args

            connection.ping(reconnect=True)
            if code == 1927 or code == 1046:
                # Connection was killed or no database selected
                connection.select_db(self.dbname)
            return query_func(connection, sql, args)

    def query(self, sql, args=None):
        self.last_n, response = self._query(sql, args, query)
        return response

    def query_many(self, sql, args):
        self.last_n, response = self._query(sql, args, query_many)
        return response

    def create(self, if_not_exists=True, db_name=None):
        db_name = db_name or self.dbname
        if_clause = 'IF NOT EXISTS' if if_not_exists else ''
        return self.query(f'CREATE DATABASE {if_clause} {db_name};')

    def use(self, db_name):
        if not self.pooling:
            self.conn.select_db(db_name)
            self.dbname = db_name
        else:
            # the following line is there to raise an exception when user is denied access
            self.pool.get_conn().select_db(db_name)
            self.pool.destroy()
            self.dbname = db_name
            self._init_pool()

    def drop(self, if_exists=True, db_name=None):
        drop_db = db_name or self.dbname
        if_clause = 'IF EXISTS' if if_exists else ''
        return self.query(f'DROP DATABASE {if_clause} {drop_db};')

    def reset(self, if_exists=True, db_name=None):
        """ALL DATA IS LOST:
        Recreate database {db_name} or {self.dbname} with no tables.
        """
        drop_db = db_name or self.dbname
        self.drop(if_exists=if_exists, db_name=drop_db)
        self.create(drop_db)
        if db_name == self.dbname:
            self.use(self.dbname)

    def databases(self):
        return [record[0] for record in self.query('SHOW DATABASES;')]

    def tables(self, db_name=None):
        db_name = db_name if db_name else self.dbname
        db_name = db_name if db_name else config.DATABASE_NAME
        if not db_name:
            raise ValueError('No database given (not even dbname was set in the config file).')
        return [record[0] for record in self.query(f'SHOW TABLES FROM {config.DATABASE_NAME};')]

    def setup(self, db_name=None):
        db_name = db_name if db_name else self.dbname
        db_name = db_name if db_name else config.DATABASE_NAME
        if not db_name:
            raise ValueError('No database given (not even dbname was set in the config file).')
        databases = self.databases()
        if db_name not in databases:
            self.create(if_not_exists=False, db_name=db_name)
