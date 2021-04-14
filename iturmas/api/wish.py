from flask import Blueprint, request, session, Response, jsonify
from iturmas.decorators import login_required
from models import CourseApplication, ClassApplication

bp = Blueprint('wish', __name__)


@bp.route('/courses/<course_code>', methods=['DELETE'])
@login_required(roles='student')
def give_up_course(course_code):
    student_code = session.user.code
    records = CourseApplication.filter(order_by='preference', student_code=student_code)
    codes = [record[0] for record in records if record[0] != course_code]
    CourseApplication.clear(student_code)
    for i, code in enumerate(codes):
        application = CourseApplication(course_code=code, student_code=student_code, preference=i)
        application.save()
    return Response(status=201)


@bp.route('/courses', methods=['POST'])
@login_required(roles='student')
def set_courses_preference():
    student_code = session.user.code
    CourseApplication.clear(student_code)
    for i, code in enumerate(request.json):
        application = CourseApplication(course_code=code, student_code=student_code, preference=i)
        application.save()
    return Response(status=201)


@bp.route('/classes/<course_code>', methods=['POST'])
@login_required(roles='student')
def set_classes_preference(course_code):
    student_code = session.user.code
    ClassApplication.clear(student_code, course_code)
    for i, code in enumerate(request.json):
        application = ClassApplication(course_code=code, class_code=code, student_code=student_code, preference=i)
        application.save()
    return Response(status=201)


@bp.route('/courses')
@login_required(roles='student')
def get_courses_preference():
    student_code = session.user.code
    records = CourseApplication.filter(order_by='preference', student_code=student_code)
    column_names = CourseApplication.column_names
    response = [{key: record[i] for i, key in enumerate(column_names)} for record in records]
    return jsonify(response), 200


@bp.route('/classes/<course_code>')
@login_required(roles='student')
def get_classes_preference(course_code):
    student_code = session.user.code
    records = ClassApplication.filter(order_by='preference', student_code=student_code, course_code=course_code)
    column_names = ClassApplication.column_names
    response = [{key: record[i] for i, key in enumerate(column_names)} for record in records]
    return jsonify(response), 200
