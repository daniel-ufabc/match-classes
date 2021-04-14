from flask import Blueprint, request, Response, session, jsonify

import config
from iturmas.myemail import send_password_reset_email
from models import Student
from models.user import User
from models.session import Session
from iturmas.decorators.auth import login_required, clear_session

bp = Blueprint('auth', __name__, template_folder='templates/auth')


@bp.route('/request_define_password')
def request_define_password():
    try:
        email = request.args['email']
    except KeyError:
        return jsonify({'error': 'Missing email field.'}), 400

    user = User.find_one(email=email)
    if not user:
        student = Student.find_one(email=email)
        if not student:
            return jsonify({'error': 'Email não registrado no sistema.'}), 400
        user = User(email=email, password='', role='student')
        user.save()

    send_password_reset_email(user)
    return jsonify({'status': 'sending email'}), 200

# @bp.route('/signup', methods=['POST'])
# def signup():
#     try:
#         data = {
#             'role': 'student',
#             'email': request.json['email'],
#             'password': generate_password_hash(request.json['password'], salt_length=16),
#             'code': request.json['code']
#         }
#     except KeyError as e:
#         return jsonify({
#             'error': 'Missing field(s).',
#             'detail': str(e)
#         }), 400
#
#     email = data['email']
#     if User.find_one(email=email):
#         time.sleep(2)
#         return jsonify({
#             'error': 'There is already an account with the given e-mail.'
#         }), 400
#
#     new_user = User(**data)
#     new_user.save()
#
#     s = Session(email=email)
#     s.save()
#
#     session['token'] = s.token
#     session['email'] = email
#
#     return Response(status=201)


@bp.route('/login', methods=['POST'])
def login():
    try:
        email = request.json['email']
        password = request.json['password']
    except KeyError as e:
        return jsonify({'error': 'Missing field(s).', 'details': str(e)}), 401

    try:
        if email != 'admin':
            user = User.find_one(email=email)
            if not user or not user.check_password(password):
                raise ValueError()
            role = user.role
        else:
            role = 'admin'
            if password != config.ADMIN_PASSWORD:
                raise ValueError()

        s = Session(email=email, role=role)
        s.save()

        session['token'] = s.token
        session['email'] = email

        return Response(status=200)
    except ValueError:
        return Response(status=401)


@bp.route('/logout')
@login_required()
def auth_logout():
    email = session['email']
    token = session['token']
    s = Session.find_one(email=email, token=token)
    if s:
        s.remove()
    clear_session(api_route=True)
    return Response(status=200)
