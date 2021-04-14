from storage import Database
from models import inject_database, Student

db = Database(db_user='root', db_password='mysql_root_password', pooling=False, autocommit=True)


# Setup for all tests
"""create_tables() should create 5 tables"""
databases = [record[0] for record in db.query('SHOW DATABASES;')]
if 'testing' in databases:
    db.query(f'DROP DATABASE IF EXISTS testing;')
    databases = [record[0] for record in db.query('SHOW DATABASES;')]
assert 'testing' not in databases
db.create('testing')
db.use('testing')

inject_database()

records = db.query('SHOW TABLES;')
tables = sorted(record[0] for record in records)
assert tables == sorted([
    'class_applications',
    'course_applications',
    'classes',
    'courses',
    'students'
])


def test_save():
    """query_many() should insert two students now"""
    students = [
        {
            'name': 'Alice',
            'code': 1,
            'max_load': 20,
        },
        {
            'name': 'Bob',
            'code': 2,
            'max_load': 16,
        },
        {
            'name': 'Euler',
            'code': 5,
            'max_load': 20,
        },
        {
            'name': 'Fred',
            'code': 6,
            'max_load': 22
        }
    ]

    for student in students:
        Student(**student).save()

    assert db.query('SELECT COUNT(*) FROM students;')[0][0] == 4

