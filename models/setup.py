from .user import User
from .session import Session
from .student import Student
from .course import Course
from .turma import Turma
from .course_application import CourseApplication
from .class_application import ClassApplication
from dependencies.mariadb import db

mapping = {
    'users': User,
    'sessions': Session,
    'students': Student,
    'courses': Course,
    'classes': Turma,
    'course_applications': CourseApplication,
    'class_applications': ClassApplication
}

tables = db.tables()
for table_name in mapping.keys():
    if table_name not in tables:
        mapping[table_name].create_table()
