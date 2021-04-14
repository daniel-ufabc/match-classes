from models.application import Application


class CourseApplication(Application):
    primary_key = 'student_code, course_code'
    table_name = 'course_applications'
    column_names = ['course_code', 'student_code', 'preference']
    column_types = ['VARCHAR(30) REFERENCES courses(code)', 'VARCHAR(30) REFERENCES students(code)', int]
    column_titles = ['CÓDIGO DA DISCIPLINA', 'RA', 'PREFERÊNCIA']
    searchable = ['course_code', 'student_code']
    has_properties = False

    @classmethod
    def clear(cls, student_code):
        query_test = '''
        DELETE FROM course_applications
        WHERE student_code = %(student_code)s;
        '''
        cls.db.query(query_test, {
            'student_code': student_code
        })
