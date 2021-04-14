from os import environ, getcwd
# from dotenv import load_dotenv
# from os import path
# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))

# For local development
APP_ROOT = environ.get('APP_ROOT') or getcwd()

# python -m smtpd -n -c DebuggingServer localhost:8025
MAIL_SERVER = environ.get('MAIL_SERVER') or 'localhost'
MAIL_PORT = int(environ.get('MAIL_PORT') or 8025)
MAIL_ADMIN_EMAIL = environ.get('MAIL_ADMIN_EMAIL') or 'admin@iturmas.com.br'
MAIL_SUPPRESS_SEND = environ.get('MAIL_SUPPRESS_SEND') or False
MAIL_DEBUG = int(environ.get('MAIL_DEBUG') or 0)
DEBUG = environ.get('DEBUG') or False
TESTING = environ.get('TESTING') or False

# Redis
REDIS_URL = environ.get('REDIS_URL') or '127.0.0.1'

# MariaDB
DATABASE_HOST = environ.get('DATABASE_HOST') or 'localhost'
DATABASE_USER = environ.get('MYSQL_USER') or 'python'
DATABASE_PASSWORD = environ.get('MYSQL_PASSWORD') or 'mysql_password'
DATABASE_ROOT_PASSWORD = environ.get('MYSQL_ROOT_PASSWORD') or 'mysql_root_password'
DATABASE_NAME = environ.get('MYSQL_DATABASE') or 'iturmas'
DATABASE_PORT = int(environ.get('DATABASE_PORT') or 3306)
DATABASE_CHARSET = environ.get('DATABASE_CHARSET') or 'utf8mb4'
DATABASE_CONNECTION_POOL_SIZE = int(environ.get('DATABASE_CONNECTION_POOL_SIZE') or 100)

# default password to clear database: 'reset'
# from werkzeug.security import generate_password_hash as gph; gph('reset',  salt_length=16)
DATABASE_CLEAR_PASSWORD_HASH = environ.get('DATABASE_CLEAR_PASSWORD_HASH') or \
    'pbkdf2:sha256:150000$E10EoZ7l8AVOO9yW$51c4f7c86938f992794' \
    'd4622948ac7365ab105ce9a140ca2e3d8c448afb797b3'

# CSV
CSV_DELIMITER = ','
CSV_QUOTECHAR = '"'

# Scheduler
DEFAULT_MAX_SEARCH = int(environ.get('DEFAULT_MAX_SEARCH') or 10)
DEFAULT_PARAMETER = 0

# Folders
ABSOLUTE_DATA_SUBDIR = environ.get('ABSOLUTE_DATA_SUBDIR') or (APP_ROOT + '/misc/data')

# CRUD
CRUD_DOMAINS = ['students', 'courses', 'classes', 'users']

# Validation
REQUIRED_PROPERTIES = {
    'classes': ['PROFESSOR', 'CARGA', 'CRITERIO'],
    'courses': [],
    'students': ['CR']
}

PROPERTIES_TO_SHOW = {
    'classes': ['PROFESSOR', 'CARGA', 'CRITERIO'],
    'courses': [],
    'students': ['CR']
}

SECRET_KEY = environ.get('SECRET_KEY') or 'Do not use this as a secret!'
ADMIN_PASSWORD = environ.get('ADMIN_PASSWORD') or 'admin'

SCHEDULER_RUNNING_FILE = environ.get('SCHEDULER_RUNNING_FILE') or 'running.txt'
SCHEDULER_OUTPUT_FILE = environ.get('SCHEDULER_OUTPUT_FILE') or 'log.txt'
SCHEDULER_ERROR_FILE = environ.get('SCHEDULER_ERROR_FILE') or 'error.txt'
SCHEDULER_RESULT_FILE = environ.get('SCHEDULER_RESULT_FILE') or 'tabelas.zip'
SCHEDULER_EXECUTE_FILE = APP_ROOT + (environ.get('SCHEDULER_EXECUTE_FILE') or '/driver/execute.py')
SCHEDULER_EXECUTE_MODULE = 'driver.execute'

# External binary dependencies
SCHEDULER_BINARY_FILENAME = APP_ROOT + (environ.get('SCHEDULER_BINARY_FILENAME') or '/driver/bin/match')
SORT_STUDENTS_BINARY_FILENAME = APP_ROOT + (environ.get('SORT_STUDENTS_BINARY_FILENAME') or '/driver/bin/sort_students')
