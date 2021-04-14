import json
from storage import Database
from pymysql.cursors import DictCursor

db = Database(pooling=False, autocommit=True, cursor_class=DictCursor)


def get_courses_and_classes_data():
    classes_of_course = dict()
    classes = dict()
    criteria = set()

    records = db.query('''
    SELECT 
        courses.code AS course_code, 
        classes.code AS class_code,
        classes.properties AS properties,
        classes.schedule AS schedule,
        classes.vacancies AS vacancies,
        classes.criterion AS criterion
    FROM classes
    INNER JOIN courses 
        ON classes.course_code = courses.code
    ''')
    for record in records:
        course_code = record['course_code']
        class_code = record['class_code']

        if course_code not in classes_of_course:
            classes_of_course[course_code] = list()
        classes_of_course[course_code].append(class_code)

        properties = record['properties']
        schedule = record['schedule']
        vacancies = record['vacancies']
        criterion = record['criterion']

        if class_code not in classes:
            classes[class_code] = dict()

        properties_obj = json.loads(properties)
        criteria_expr = criterion.strip().replace(' ', '').replace('\t', '')
        classes[class_code]['criteria'] = criteria_expr
        classes[class_code]['vacancies'] = vacancies
        classes[class_code]['load'] = properties_obj['CARGA']
        classes[class_code]['schedule'] = schedule

        if criteria_expr:
            criteria.add(criteria_expr)

    return classes_of_course, classes, list(criteria)


def get_students():
    students = dict()
    carga = dict()

    records = db.query('''
    SELECT code, properties, max_load 
    FROM students
    INNER JOIN class_applications 
        ON students.code = class_applications.student_code
    INNER JOIN course_applications
        ON students.code = course_applications.student_code 
            AND course_applications.course_code = class_applications.course_code
    ''')
    for record in records:
        code = record['code']
        properties = record['properties']
        carga[code] = record['max_load']
        if code not in students:
            students[code] = json.loads(properties)

    return students, carga


def get_applications():
    course_apps = dict()

    records = db.query('''SELECT student_code, course_code
    FROM course_applications 
    ORDER BY preference ASC''')
    for record in records:
        student = record['student_code']
        if student not in course_apps:
            course_apps[student] = list()
        course_apps[student].append(record['course_code'])

    class_apps = dict()

    records = db.query('''
    SELECT 
        student_code, 
        course_code, 
        class_code
    FROM class_applications 
    ORDER BY preference ASC
    ''')
    for record in records:
        student = record['student_code']
        course = record['course_code']
        if student not in class_apps:
            class_apps[student] = dict()
        if course not in class_apps[student]:
            class_apps[student][course] = list()
        class_apps[student][course].append(record['class_code'])

    return course_apps, class_apps


def get_parameters(criteria_list):
    parameters = set()
    for expr in criteria_list:
        for param in expr.split('>'):
            parameters.add(param.strip())

    return sorted(parameters)
