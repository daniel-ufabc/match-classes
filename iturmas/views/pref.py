import json

import pymysql
from flask import Blueprint, session, request, render_template, url_for, redirect, jsonify, flash
from iturmas.decorators import login_required
from storage import Database
from models import Student

db = Database(pooling=True, autocommit=False, cursor_class=pymysql.cursors.DictCursor)
bp = Blueprint('pref', __name__)

# legacy code not totally refactored...


@bp.route('/main')
@login_required(roles='student', api_route=False, get_user=True)
def pref_main():
    email = session.user.email
    student = Student.find_one(email=email)
    if not student:
        flash(f'O aluno registrado com o email "{email}" não consta mais no banco de dados.')
        return redirect(url_for('pages.login'))
    student_code = student.code

    course_list = db.query('''
        SELECT 
            ca.course_code AS course_code,
            ca.preference AS preference,
            c.properties AS properties,
            c.name as name
        FROM course_applications ca
        INNER JOIN courses c ON ca.course_code = c.code
        WHERE ca.student_code = %s
        ORDER BY preference ASC
        ''', student_code)

    classes = db.query('''
        SELECT 
            ca.class_code AS class_code,
            ca.course_code AS course_code,
            ca.preference AS preference,
            c.properties AS properties,
            c.schedule AS schedule
        FROM class_applications ca
        INNER JOIN classes c ON ca.class_code = c.code
        WHERE ca.student_code = %s
        ORDER BY preference ASC
        ''', student_code)

    class_lists = {course_app['course_code']: list() for course_app in course_list}
    for class_app in classes:
        course_code = class_app['course_code']
        if course_code not in class_lists:
            continue
        class_lists[course_code].append(class_app)

    return render_template('students/main.html', course_list=course_list, class_lists=class_lists)


@bp.route('/give_up', methods=['POST'])
@login_required(roles='student', get_user=True)
def pref_give_up():
    email = session.user.email
    student = Student.find_one(email=email)
    student_code = student.code
    data = request.form
    course_code = data['courseCode']
    next_pages = data['nextPages']

    query_delete = '''
    DELETE FROM course_applications
    WHERE course_code = %s AND student_code = %s
    '''

    with db.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query_delete, [course_code, student_code])

    if next_pages:
        i = next_pages.find(',')
        next_page, next_pages = (next_pages, '') if i < 0 else (next_pages[:i], next_pages[i+1:])
        return pref_set(course_code=next_page, next_pages=next_pages)

    return redirect(url_for('pref.pref_main'))


@bp.route('/set')
@bp.route('/set/<course_code>')
@login_required(roles='student', get_user=True)
def pref_set(course_code='', next_pages=''):
    email = session.user.email
    student = Student.find_one(email=email)
    student_code = student.code
    if course_code:
        query = '''
            SELECT code, name
            FROM courses
            WHERE code = '{course_code}'
        '''.format(course_code=course_code)

        with db.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                course_data = cursor.fetchone()
                search_header = f'Filtrar turmas da disciplina "{course_data["name"]}"' if course_data else \
                    'Disciplina não encontrada'

            query = '''
            SELECT 
                ca.preference AS preference,
                ca.course_code AS course_code, 
                ca.class_code AS class_code, 
                c.schedule AS schedule,
                c.properties AS properties
            FROM class_applications ca
            INNER JOIN classes c ON ca.class_code = c.code
            WHERE ca.student_code = '{student_code}' AND ca.course_code = '{course_code}' 
            ORDER BY preference ASC
            '''.format(student_code=student_code, course_code=course_code)

            with connection.cursor() as cursor:
                cursor.execute(query)
                preselected = list(cursor.fetchall())

        search_bar_hint_text = 'turno, código, etc.'
        selected_items_header = 'Turmas pré-selecionadas'

    else:
        query = '''
        SELECT 
            ca.preference AS preference,
            ca.course_code AS course_code, 
            c.name AS name,
            c.properties AS properties
        FROM course_applications ca
        INNER JOIN courses c ON ca.course_code = c.code
        WHERE ca.student_code = '{student_code}' 
        ORDER BY preference ASC
        '''.format(student_code=student_code, course_code=course_code)

        with db.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                preselected = list(cursor.fetchall())

        search_header = 'Filtrar disciplinas:'
        search_bar_hint_text = 'nome ou código'
        selected_items_header = 'Disciplinas pré-selecionadas'

    return render_template('students/addnsort.html', next_pages=next_pages,
                           course_code=course_code, search_header=search_header,
                           search_bar_hint_text=search_bar_hint_text,
                           selected_items_header=selected_items_header,
                           preselected=preselected)


@bp.route('/save', methods=['POST'])
@login_required(roles='student', get_user=True)
def pref_save():
    email = session.user.email
    student = Student.find_one(email=email)
    student_code = student.code
    data = request.form
    course_code = data['courseCode']
    next_pages = data['nextPages']
    sequence = json.loads(data['sequence'])

    if course_code:
        # query to save preferences among classes of a course
        values = [f"('{course_code}', '{code}', '{student_code}', {i})" for i, code in enumerate(sequence)]
        delete_query = '''
        DELETE 
        FROM class_applications
        WHERE student_code = '{student_code}' AND course_code = '{course_code}'
        '''.format(student_code=student_code, course_code=course_code)

        insert_query = '''
        INSERT INTO class_applications 
            (course_code, class_code, student_code, preference)
        VALUES 
        ''' + ', '.join(values)

    else:
        # query to save preferences among courses
        values = [f"('{code}', '{student_code}', {i})" for i, code in enumerate(sequence)]
        delete_query = '''
        DELETE 
        FROM course_applications
        WHERE student_code = '{student_code}'
        '''.format(student_code=student_code)

        insert_query = '''
        INSERT INTO course_applications 
            (course_code, student_code, preference)
        VALUES 
            ''' + ', '.join(values) + ';'

    with db.connection() as connection:
        with connection.cursor() as cursor:
            # run (whichever) query to save preferences
            cursor.execute(delete_query)
            if values:
                # only if sequence is not empty
                print(insert_query)
                cursor.execute(insert_query)

        if not course_code:
            # find courses without class preferences
            query_missing_pref = '''
            SELECT course_code
            FROM course_applications
            WHERE student_code = '{student_code}'
            EXCEPT 
            SELECT course_code
            FROM class_applications
            WHERE student_code = '{student_code}'
            '''.format(student_code=student_code)

            with connection.cursor() as cursor:
                cursor.execute(query_missing_pref)
                next_pages = ','.join([row['course_code'] for row in cursor.fetchall()])

    if next_pages:
        i = next_pages.find(',')
        next_page, next_pages = (next_pages, '') if i < 0 else (next_pages[:i], next_pages[i+1:])
        return pref_set(course_code=next_page, next_pages=next_pages)

    return redirect(url_for('pref.pref_main'))


@bp.route('/search', methods=['POST'])
@login_required(roles='student')
def search():
    data = request.form

    try:
        ss = data['search_string']
        offset = int(data['offset'])
        maxperpage = int(data['max_per_page'])
        course_code = data['extra']
    except (KeyError, ValueError):
        return 'Bad request.', 400

    # DEBUG
    print(dict(data), course_code)

    if course_code:
        count_query = '''
        SELECT COUNT(*) AS count
        FROM  classes 
        INNER JOIN courses
        ON classes.course_code = courses.code
        WHERE classes.course_code = '{course_code}' AND 
            (courses.name LIKE '%{ss}%' 
            OR classes.code LIKE '%{ss}%' 
            OR classes.properties LIKE '%{ss}%')
        '''.format(ss=ss, course_code=course_code)
    else:
        count_query = '''
        SELECT COUNT(DISTINCT co.name, co.code, co.properties) AS count
        FROM  courses co
        INNER JOIN classes ca
            ON co.code = ca.course_code
        WHERE co.name LIKE '%{ss}%' 
            OR co.code LIKE '%{ss}%'
        '''.format(ss=ss)

    with db.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(count_query)
            total = cursor.fetchone()['count']

    result = dict()
    result['total'] = total
    if offset >= total:
        offset = total - 1 if total > 0 else 0
    offset = offset - offset % maxperpage
    result['offset'] = offset

    if course_code:
        query = '''
        SELECT * 
        FROM  classes 
        INNER JOIN courses
            ON classes.course_code = courses.code
        WHERE classes.course_code = '{course_code}' AND 
            (courses.name LIKE '%{ss}%' 
            OR classes.code LIKE '%{ss}%' 
            OR classes.properties LIKE '%{ss}%')
        ORDER BY courses.name, classes.code ASC
        LIMIT {offset}, {maxperpage}    
        '''.format(ss=ss, offset=offset, maxperpage=maxperpage, course_code=course_code)
    else:
        query = '''
        SELECT DISTINCT co.name AS name, co.code AS code, co.properties AS properties
        FROM  courses co
        INNER JOIN classes ca
            ON co.code = ca.course_code
        WHERE co.name LIKE '%{ss}%' 
            OR co.code LIKE '%{ss}%'
        ORDER BY co.name ASC
        LIMIT {offset}, {maxperpage}    
        '''.format(ss=ss, offset=offset, maxperpage=maxperpage)

    with db.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result['items'] = cursor.fetchall()

    html_filename = 'class' if course_code else 'course'
    html_filename += '_pref_range.html'

    result['entries'] = render_template(html_filename, records=result['items'])

    return jsonify(result), 200
