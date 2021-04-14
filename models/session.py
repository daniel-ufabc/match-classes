from time import time
from models.base import Base
from utils.misc import get_token


class Session(Base):
    email: str
    token: str
    role: str
    primary_key = 'email, token'
    table_name = 'sessions'
    column_names = ['email', 'token', 'timestamp', 'role']
    column_types = [str, str, 'VARCHAR(30)', 'VARCHAR(30)']
    column_titles = ['EMAIL', 'TOKEN', 'TIMESTAMP', 'ROLE']
    has_properties = False

    def __init__(self, email, token=None, timestamp=None, role=None):
        token = token if token else get_token()
        timestamp = timestamp if timestamp else time()
        super().__init__(email=email, token=token, timestamp=timestamp, role=role)

    @classmethod
    def remove_all_from_user(cls, email):
        cls.db.query(f"DELETE FROM sessions WHERE email = %s;", email)
