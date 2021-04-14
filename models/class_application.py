from models.application import Application


class ClassApplication(Application):
    primary_key = 'student_code, course_code, class_code'
    table_name = 'class_applications'
    column_names = ['course_code', 'class_code', 'student_code', 'preference']
    column_types = [
        'VARCHAR(30) REFERENCES courses(code)',
        'VARCHAR(30) REFERENCES classes(code)',
        'VARCHAR(30) REFERENCES students(code)',
        int
    ]
    column_titles = [
        'CÓDIGO DA DISCIPLINA',
        'CÓDIGO DA TURMA',
        'RA',
        'PREFERÊNCIA'
    ]
    searchable = ['student_code', 'class_code', 'course_code']
    has_properties = False

    @classmethod
    def clear(cls, student_code, course_code):
        query_test = '''
            DELETE FROM class_applications
            WHERE student_code = %(student_code)s AND course_code = %(course_code)s;
            '''
        cls.db.query(query_test, {
            'student_code': student_code,
            'course_code': course_code
        })
