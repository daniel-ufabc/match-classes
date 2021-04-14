from models.base import Base


class Application(Base):
    @classmethod
    def import_csv(cls, filename, row_iterator=None, contains_header=True,
                   clear_table=False, ignore=True, on_duplicate_key_update=False):
        super().import_csv(filename, row_iterator=row_iterator, contains_header=contains_header,
                           clear_table=True, ignore=ignore, on_duplicate_key_update=on_duplicate_key_update)

    @classmethod
    def count(cls, search_string=''):
        return cls.db.query('''
            SELECT COUNT(DISTINCT students.code)
            FROM students
            INNER JOIN course_applications
            ON students.code = course_applications.student_code;
            ''')[0][0]
