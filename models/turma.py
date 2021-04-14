from models.base import Base


# Using the portuguese name in order to avoid conflict with reserved keyword 'class'
class Turma(Base):
    primary_key = 'code'
    table_name = 'classes'
    column_names = [
        'code',
        'course_code',
        'schedule',
        'vacancies',
        'criterion',
        'properties'
    ]
    column_types = [
        'VARCHAR(30)',
        'VARCHAR(30) REFERENCES courses(code)',
        str,
        int,
        str,
        dict
    ]
    column_titles = [
        'CÓDIGO DA TURMA',
        'CÓDIGO DA DISCIPLINA',
        'HORÁRIOS',
        'VAGAS',
        'CRITÉRIO',
        'PROPRIEDADES'
    ]
    searchable = ['code', 'course_code', 'properties']
    has_properties = True

    # @classmethod
    # def count(cls, search_string=''):
    #     where_clause = cls._where_clause(search_string)
    #     return cls.db.query(f'''
    #         SELECT COUNT(*) FROM classes
    #         INNER JOIN courses ON classes.course_code = courses.code
    #         {where_clause};
    #         ''',
    #         {
    #             'search_string': f'%{search_string}%' if search_string else ''
    #         }
    #     )[0][0]
    #
    # @classmethod
    # def _search_query(cls, search_string, order_by='', ascending=True, limit_offset=(0, 0)):
    #     where_clause = cls._where_clause(search_string)
    #     order_by_clause = cls._order_by_clause()
    #     limit, offset = limit_offset
    #     limit, offset = int(limit), int(offset)
    #     limit_clause = f'LIMIT {offset}, {limit}' if limit else ''
    #     return f'''
    #     SELECT
    #         classes.code,
    #         courses.code,
    #         classes.schedule,
    #         classes.vacancies,
    #         classes.criterion,
    #         classes.properties,
    #         courses.name
    #     FROM classes
    #     INNER JOIN courses ON classes.course_code = courses.code
    #     {where_clause}
    #     {order_by_clause}
    #     {limit_clause};
    #     '''
    #
    # @classmethod
    # def _where_clause(cls, search_string):
    #     if not search_string:
    #         return ''
    #     return f"""
    #     WHERE courses.name LIKE %(search_string)s OR classes.code LIKE %(search_string)s
    #         OR courses.code LIKE %(search_string)s OR classes.properties LIKE %(search_string)s
    #     """
    #
    # @classmethod
    # def _order_by_clause(cls, order_by='', ascending=True):
    #     return 'ORDER BY courses.name, classes.code ASC'

    @classmethod
    def search_from_course(cls, search_string, course_code, limit_offset=(0, 0)):
        limit, offset = limit_offset
        limit, offset = int(limit), int(offset)
        limit_clause = f'LIMIT {offset}, {limit}' if limit else ''
        where_clause = 'WHERE classes.course_code = %(course_code)s' + ''' 
            AND (courses.name LIKE %(search_string)s 
            OR classes.code LIKE %(search_string)s 
            OR classes.properties LIKE %(search_string)s)''' if search_string else ''
        query_string = f'''
        SELECT
            classes.code, 
            courses.code, 
            classes.schedule, 
            classes.vacancies, 
            classes.criterion, 
            classes.properties,
            courses.name
        FROM  classes 
        INNER JOIN courses
            ON classes.course_code = courses.code
        {where_clause}
        ORDER BY courses.name, classes.code ASC
        {limit_clause};
        '''
        return cls.db.query(query_string, {
            'search_string': f'%{search_string}%' if search_string else '',
            'course_code': course_code
        })
