import csv
from time import time

import jwt
from flask import current_app

import config
from models.base import Base
from werkzeug.security import check_password_hash

from utils.files import data_filename


class User(Base):
    primary_key = 'email'
    table_name = 'users'
    column_names = ['email', 'password', 'role']
    column_types = [str, str, 'VARCHAR(30)']
    column_titles = ['EMAIL', 'SENHA', 'ACESSO']
    has_properties = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email = self.email.strip().lower()
        if not self.password:
            self.password = ''
        self.role = self.role.strip().lower()

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_data(self):
        data = super().get_data()
        data.pop('password', None)
        return data

    @classmethod
    def export_csv(cls, basename=None):
        """
        Exports the data of the corresponding table to a file in the csv format.

        :param basename: If omitted, it will be generated from the name of
        the table (cls.table_name) and from the variable data_subdir in the
        config file.
        :return: The name of the file where the data was saved.
        """
        if basename is None:
            basename = f'{cls.table_name}.{time()}.csv'
        fullname = data_filename(basename)

        records = cls.db.query(f"SELECT `email`, 'não disponível', `role` FROM {cls.table_name};")
        with open(fullname, 'w') as f:
            writer = csv.writer(f, delimiter=config.CSV_DELIMITER, quotechar=config.CSV_QUOTECHAR,
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(cls.column_titles)
            for record in records:
                writer.writerow(record)

        return basename

    @classmethod
    def default_row_iterator(cls, header, rows):
        for row in rows:
            # passwords are ignored
            # new users get an e-mail with a link to set a password
            yield row[0], '', row[2]

    @classmethod
    def import_csv(cls, filename, row_iterator=None, contains_header=True,
                   clear_table=False, ignore=True, on_duplicate_key_update=False):

        assert ignore, 'Should ignore entries with duplicate keys for table "users".'
        assert not on_duplicate_key_update, 'Cannot update entries for table "users".'
        assert not clear_table, 'Cannot clear table "users" while performing a batch insert.'

        temp_table = f'{cls.table_name}_tmp'

        with cls.db.connection(ping=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f'CREATE TEMPORARY TABLE {temp_table} LIKE {cls.table_name};')

            with connection.cursor() as cursor:
                cursor.execute(f'DROP INDEX `PRIMARY` ON {temp_table};')

            columns, placeholders = cls._columns_and_placeholders()
            columns_text = ', '.join(columns)
            values_text = ', '.join(['%s' for _ in placeholders])

            with open(filename) as f:
                rows = csv.reader(f, delimiter=config.CSV_DELIMITER, quotechar=config.CSV_QUOTECHAR)
                header = next(rows) if contains_header else None
                if row_iterator is None:
                    row_iterator = cls.default_row_iterator
                with connection.cursor() as cursor:
                    n_read = cursor.executemany(f'''
                    INSERT INTO {temp_table} ({columns_text}) VALUES ({values_text});
                    ''', row_iterator(header, rows))

            with connection.cursor() as cursor:
                cursor.execute(f'SELECT COUNT(*) FROM {cls.table_name};')
                n_before = cursor.fetchone()[0]

            with connection.cursor() as cursor:
                query_text = f'''
                INSERT IGNORE INTO {cls.table_name}
                SELECT {columns_text} FROM {temp_table};
                '''

                cursor.execute(query_text)

            with connection.cursor() as cursor:
                cursor.execute(f'SELECT COUNT(*) FROM {cls.table_name};')
                n_after = cursor.fetchone()[0]

            with connection.cursor() as cursor:
                cursor.execute(f'DROP TEMPORARY TABLE {temp_table};')

            # returns (number of newly inserted rows, number of duplicate/updated entries)
            response = {'new': n_after - n_before, 'duplicate': n_read - (n_after - n_before)}
            return response

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.email, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # noinspection PyBroadException
    @staticmethod
    def verify_reset_password_token(token):
        try:
            email = jwt.decode(token, current_app.config['SECRET_KEY'],
                               algorithms=['HS256'])['reset_password']
        except:
            return

        return User.find_one(email=email)
