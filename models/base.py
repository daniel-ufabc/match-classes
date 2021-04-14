import csv
import json
from json import JSONDecodeError
from time import time

import config
from dependencies.mariadb import db
from utils.files import data_filename


class Base:
    db = db
    primary_key = 'id'
    table_name = ''
    column_names = list()
    column_types = list()
    column_titles = list()
    searchable = list()
    has_properties = False

    def __new__(cls, *args, **kwargs):
        assert cls.db is not None, 'Please, use inject_database() to satisfy dependency.'
        primary_key_columns = cls.primary_keys()
        assert cls.primary_key == 'id' or set(primary_key_columns).issubset(cls.column_names), \
            'Primary key must be contained in column_names if it is not "id".'
        if cls.has_properties:
            assert 'properties' == cls.column_names[-1], 'The last field in column_names must be "properties".'
            assert cls.column_types[-1] is dict, \
                'The entry in column_types that corresponds to "properties" must be dict.'
        return object.__new__(cls)

    def __init__(self, **kwargs):
        cls = type(self)
        required_attributes = set(cls.column_names) - {'properties'}
        assert required_attributes.issubset(kwargs.keys()), 'Missing attributes'
        for key, value in kwargs.items():
            setattr(self, key, value)
        if cls.has_properties and hasattr(self, 'properties'):
            if type(self.properties) == str:
                try:
                    self.properties = json.loads(self.properties)
                except JSONDecodeError as e:
                    self.properties = {'JSONDecodeError': str(e), 'string': self.properties}

    @classmethod
    def primary_keys(cls):
        return [column.strip() for column in cls.primary_key.split(',')]

    def _on_duplicate_query_part(self):
        cls = type(self)
        updatable = list()
        for column in cls.column_names:
            if hasattr(self, column) and column != cls.primary_key:
                value = Base.format_value(getattr(self, column))
                updatable.append(f"`{column}` = '{value}'")
        return ' ON DUPLICATE KEY UPDATE ' + ', '.join(updatable)

    def prepare(self):
        """Trim / adjust / cleanup data before saving into the database."""
        pass

    def save(self, on_duplicate_key_update=False):
        self.prepare()
        cls = type(self)
        query_text = cls._insert_query_prefix()
        if on_duplicate_key_update:
            query_text += self._on_duplicate_query_part()
        query_text += ';'
        data = {column: Base.format_value(getattr(self, column, None))
                for column in cls.column_names}
        if cls.has_properties:
            data['properties'] = Base.format_value(getattr(self, 'properties', dict()))
        cls.db.query(query_text, data)

    def get_data(self):
        cls = type(self)
        data = {key: getattr(self, key) for key in self.__dict__ if key in cls.column_names}
        if cls.has_properties:
            data['properties'] = json.dumps(data.get('properties', dict()), ensure_ascii=False)
        return data

    @classmethod
    def _columns_and_placeholders(cls):
        if not hasattr(cls, 'prepared_columns_and_placeholders'):
            columns, placeholders = list(), list()
            for column in cls.column_names:
                columns.append(f'`{column}`')
                placeholders.append(f"%({column})s")

            cls.prepared_columns_and_placeholders = [columns, placeholders]

        return cls.prepared_columns_and_placeholders

    @classmethod
    def _insert_query_prefix(cls):
        if not hasattr(cls, 'prepared_insert_query_prefix'):
            columns, placeholders = cls._columns_and_placeholders()
            columns_text, values_text = ', '.join(columns), ', '.join(placeholders)
            cls.prepared_insert_query_prefix = f'INSERT INTO `{cls.table_name}` ({columns_text}) VALUES ({values_text})'

        return cls.prepared_insert_query_prefix

    @classmethod
    def create_table(cls):
        assert cls.column_names
        assert len(cls.column_names) == len(cls.column_types)
        assert cls.table_name

        columns = list()
        for key, value in zip(cls.column_names, cls.column_types):
            if value is int:
                columns.append(f'`{key}` INT')
            elif value is str:
                columns.append(f'`{key}` VARCHAR(255)')
            elif value is float:
                columns.append(f'`{key}` DOUBLE')
            elif value is dict:
                columns.append(f'`{key}` LONGTEXT')
            elif isinstance(value, str):
                columns.append(f'`{key}` {value}')

        if cls.primary_key == 'id' and 'id' not in cls.column_names:
            columns.append('`id` INT NOT NULL AUTO_INCREMENT')

        columns_text = ', '.join(columns)
        query_string = f'''
        CREATE TABLE IF NOT EXISTS {cls.table_name} 
        ({columns_text}, PRIMARY KEY ({cls.primary_key}))
        ENGINE=InnoDB CHARACTER SET {config.DATABASE_CHARSET};
        '''

        return cls.db.query(query_string)

    @classmethod
    def default_row_iterator(cls, header, rows):
        if header is None or not cls.has_properties or len(header) == len(cls.column_names) and \
                header[-1].lower() == cls.column_titles[-1].lower():
            for row in rows:
                yield row
        else:
            n = len(cls.column_names) - 1
            truncated_header = header[n:]
            for row in rows:
                yield row[:n] + [json.dumps({truncated_header[i]: element for i, element in enumerate(row[n:])},
                                            ensure_ascii=False)]

    @classmethod
    def import_csv(cls, filename, row_iterator=None, contains_header=True,
                   clear_table=False, ignore=True, on_duplicate_key_update=False):
        """
        Imports the content of a csv file into the corresponding table (cls.table_name).

        :param filename: The file that contains data to be imported.
        :param row_iterator: Iterator that pre-process each row of the file before inserting.
        :param contains_header: Whether the file contains a header row.
        :param clear_table: Whether target table must be cleared before importing the data.
        :param ignore: Whether to ignore inserting rows with duplicate key.
        :param on_duplicate_key_update: Whether to update the content of an entry in the table
        if its key matches the key of a row we are trying to insert.
        :return: Returns a pair of numbers (number of rows inserted, number of duplicate rows).
        A row with a key that matches a key already on the table will be counted in 'number
        of duplicate rows) whether it is ignored or used to update values on the table.
        """
        # TODO: add validation and treat exceptions to give proper feedback to the user!!!

        assert not (ignore and on_duplicate_key_update), \
            'import_csv(): ignore and on_duplicate_key_update cannot both be true'
        assert not (clear_table and on_duplicate_key_update), \
            'import_csv(): clear_table and on_duplicate_key_update cannot both be true'

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

            if clear_table:
                with connection.cursor() as cursor:
                    cursor.execute(f'TRUNCATE TABLE {cls.table_name};')
                n_before = 0
            else:
                with connection.cursor() as cursor:
                    cursor.execute(f'SELECT COUNT(*) FROM {cls.table_name};')
                    n_before = cursor.fetchone()[0]

            if on_duplicate_key_update:
                assignments = [f'{column} = VALUES({column})' for column
                               in cls.column_names if column != cls.primary_key]

                on_duplicate_clause = ' ON DUPLICATE KEY UPDATE ' + ', '.join(assignments)
            else:
                on_duplicate_clause = ''

            ignore_clause = 'IGNORE' if ignore else ''
            with connection.cursor() as cursor:
                query_text = f'''
                INSERT {ignore_clause} INTO {cls.table_name}
                SELECT {columns_text} FROM {temp_table} 
                {on_duplicate_clause};
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

        columns, placeholders = cls._columns_and_placeholders()
        columns_text = ', '.join(columns)

        records = cls.db.query(f'SELECT {columns_text} FROM {cls.table_name};')
        with open(fullname, 'w') as f:
            writer = csv.writer(f, delimiter=config.CSV_DELIMITER, quotechar=config.CSV_QUOTECHAR,
                                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(cls.column_titles)
            for record in records:
                writer.writerow(record)

        return basename

    @staticmethod
    def format_value(value, v_type=None):
        if v_type is None:
            v_type = type(value)

        if v_type is dict:
            formatted = json.dumps(value, ensure_ascii=False)
        elif v_type is str:
            formatted = value
        elif v_type is int or v_type is float:
            formatted = f'{value}'
        elif v_type is bytes:
            formatted = value.decode()
        else:
            formatted = 'NULL'

        return formatted

    @classmethod
    def find_one(cls, **criteria):
        allowed_keys = set(cls.column_names)
        if cls.primary_key == 'id':
            allowed_keys.add('id')
        assert set(criteria.keys()).issubset(allowed_keys), \
            f'You can only filter by fields in the table "{cls.table_name}".'
        columns, _ = cls._columns_and_placeholders()
        columns_text = ', '.join(columns)
        where_clause = ''
        if criteria:
            where_clause = 'WHERE ' + ' AND '.join(f"{key} = '{Base.format_value(value)}'" for
                                                   key, value in criteria.items())
        with cls.db.connection(ping=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT {columns_text} FROM {cls.table_name} {where_clause};')
                values = cursor.fetchone()
                if not values:
                    return None
                if cursor.fetchone():
                    raise ValueError('More than one row match the criteria.')
                fields_dict = {key: value for key, value in zip(cls.column_names, values)}
                instance = cls(**fields_dict)
                instance.unique = True
                return instance

    @classmethod
    def _where_clause(cls, search_string):
        if not search_string:
            return ''
        if not cls.searchable:
            return ''
        comparisons = [f"{column} LIKE %(search_string)s" for column in cls.searchable]
        return 'WHERE ' + ' OR '.join(comparisons)

    @classmethod
    def _join_clause(cls):
        return ''

    @classmethod
    def _order_by_clause(cls, order_by='', ascending=True):
        if not order_by:
            return ''
        order_by = order_by if isinstance(order_by, str) else ', '.join(order_by)
        asc_text = 'ASC' if ascending else 'DESC'
        order_clause = f'ORDER BY {order_by} {asc_text}' if order_by else ''
        return order_clause

    @classmethod
    def _select_clause(cls):
        columns, _ = cls._columns_and_placeholders()
        columns_text = ', '.join(columns)

        return f'SELECT {columns_text}'

    @classmethod
    def _from_clause(cls):
        return f'FROM {cls.table_name}'

    @classmethod
    def _search_query(cls, search_string, order_by='', ascending=True, limit_offset=(0, 0)):
        select_clause = cls._select_clause()
        from_clause = cls._from_clause()

        join_clause = cls._join_clause()
        where_clause = cls._where_clause(search_string)

        order_clause = cls._order_by_clause(order_by=order_by, ascending=ascending)

        limit, offset = limit_offset
        limit, offset = int(limit), int(offset)
        limit_clause = f'LIMIT {offset}, {limit}' if limit else ''

        return f'''
        {select_clause}
        {from_clause}
        {join_clause}
        {where_clause} 
        {order_clause}
        {limit_clause};
        '''

    @classmethod
    def count(cls, search_string=''):
        join_clause = cls._join_clause()
        where_clause = cls._where_clause(search_string)
        return cls.db.query(
            f'SELECT COUNT(*) FROM {cls.table_name} {join_clause} {where_clause};',
            {
                'search_string': f'%{search_string}%' if search_string else ''
            }
        )[0][0]

    @classmethod
    def search(cls, search_string, order_by='', ascending=True, limit_offset=(0, 0)):
        return cls.db.query(
            cls._search_query(search_string, order_by=order_by, ascending=ascending, limit_offset=limit_offset),
            {
                'search_string': f'%{search_string}%' if search_string else ''
            }
        )

    @classmethod
    def filter(cls, order_by='', ascending=True, **kwargs):
        order_by_clause = cls._order_by_clause(order_by=order_by, ascending=ascending)
        data = {key: value for key, value in kwargs if key in cls.column_names}
        if not data:
            raise KeyError('No valid filter for this table has been defined.')
        criteria = [f'{key} = %({key})s' for key in data]
        columns, placeholders = cls._columns_and_placeholders()
        columns_text = ', '.join(columns)
        where_clause = 'WHERE ' + ' AND '.join(criteria)
        query_string = f'''
        SELECT {columns_text}
        FROM {cls.table_name}
        {where_clause}
        {order_by_clause};
        '''
        return cls.db.query(query_string, data)

    def remove(self, ignore=True):
        cls = type(self)
        primary_key_columns = cls.primary_keys()
        for column in primary_key_columns:
            if not hasattr(self, column):
                raise ValueError('Cannot certify this object corresponds to a unique entry on the table.')
        where_clause = 'WHERE ' + ' AND '.join(f"{key} = '{getattr(self, key)}'" for key in primary_key_columns)
        ignore_clause = 'IGNORE' if ignore else ''
        with cls.db.connection(ping=True, begin=True) as connection:
            with connection.cursor() as cursor:
                n = cursor.execute(f'DELETE {ignore_clause} FROM {cls.table_name} {where_clause};')
            if n != 1:
                connection.rollback()
        if n > 1 or not ignore and n < 1:
            raise ValueError('Object does not correspond to exactly one entry on the table.')
