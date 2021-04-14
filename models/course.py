from models.base import Base


class Course(Base):
    primary_key = 'code'
    table_name = 'courses'
    column_names = ['code', 'name', 'properties']
    column_types = ['VARCHAR(30)', str, dict]
    column_titles = ['CÓDIGO DA DISCIPLINA', 'NOME', 'PROPRIEDADES']
    searchable = ['code', 'name', 'properties']
    has_properties = True

    @classmethod
    def _order_by_clause(cls, order_by='', ascending=True):
        return 'ORDER BY name ASC'

    @classmethod
    def search_if_has_classes(cls, search_string, limit_offset=(0, 0)):
        limit, offset = limit_offset
        limit_clause = f'LIMIT %(offset)s, %(limit)s' if limit else ''
        query_string = f'''
        SELECT DISTINCT courses.name, courses.code, courses.properties
        FROM  courses
        INNER JOIN classes
            ON courses.code = classes.course_code
        WHERE courses.name LIKE '%%%(search_string)s%%' 
            OR courses.code LIKE '%%%(search_string)s%%'
        ORDER BY courses.name ASC
        {limit_clause};
        '''
        return cls.db.query(query_string, {
            'search_string': search_string,
            'limit': limit,
            'offset': offset
        })
