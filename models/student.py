from models.base import Base


class Student(Base):
    primary_key = 'code'
    table_name = 'students'
    column_names = ['code', 'name', 'email', 'max_load', 'properties']
    column_types = [str, str, str, int, dict]
    column_titles = ['RA', 'NOME', 'EMAIL', 'CARGA', 'PROPRIEDADES']
    searchable = ['code', 'name', 'email', 'properties']
    has_properties = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email = self.email.strip()
        self.code = self.code.strip()
        self.name = self.name.strip()
        self.max_load = int(self.max_load)

    @classmethod
    def _order_by_clause(cls, order_by='', ascending=True):
        return 'ORDER BY name ASC'
