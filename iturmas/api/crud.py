from flask import Blueprint, request, Response, jsonify, session
from pymysql import IntegrityError

import config
from iturmas.decorators.auth import login_required
from models import mapping, Session
import json

bp = Blueprint('crud', __name__)


@bp.route('/<domain>', methods=['POST'])
@login_required(roles='admin')
def create(domain):
    if domain not in config.CRUD_DOMAINS:
        return jsonify({'error': 'invalid domain'}), 400
    cls = mapping[domain]
    data = {key: request.form.get(key, None) for key in cls.column_names}
    if domain == 'users':
        data['password'] = ''
    try:
        obj = cls(**data)
        obj.save(on_duplicate_key_update=bool(request.form.get('update', False)))
    except (AssertionError, ValueError, json.JSONDecodeError, IntegrityError) as e:
        return jsonify({'error': str(e)}), 400

    return Response(status=201)


@bp.route('/<domain>')
@login_required(roles=['student', 'admin'])
def read(domain):
    if domain not in config.CRUD_DOMAINS:
        return jsonify({'error': 'invalid domain'}), 400
    se = session.session_object
    if se.role != 'admin' and domain not in ['courses', 'classes']:
        return Response(status=403)
    cls = mapping[domain]
    try:
        data = {key: request.args[key] for key in cls.primary_keys()}
    except KeyError as e:
        return jsonify({'error': 'missing required field', 'details': str(e)}), 400
    try:
        obj = cls.find_one(**data)
        if not obj:
            return Response(status=404)
        saved_data = obj.get_data()
        return jsonify(saved_data), 200
    except (AssertionError, ValueError, json.JSONDecodeError):
        return Response(status=500)


@bp.route('/<domain>', methods=['PATCH'])
@login_required(roles='admin')
def update(domain):
    if 'update' not in request.form:
        return jsonify({'error': 'update field must be set to True'}), 400
    return create(domain)


@bp.route('/<domain>', methods=['DELETE'])
@login_required(roles='admin')
def remove(domain):
    if domain not in config.CRUD_DOMAINS:
        return jsonify({'error': 'invalid domain'}), 400
    data = dict(request.form)
    if domain == 'users' and data.get('email', '') == 'admin':
        return Response(status=403)
    try:
        cls = mapping[domain]
        obj = cls.find_one(**data)
        if not obj:
            return jsonify({'error': 'Not found.'}), 404
        obj.remove(ignore=False)
        if domain == 'users':
            Session.remove_all_from_user(obj.email)
        return jsonify(obj.get_data()), 200
    except (AssertionError, ValueError, json.JSONDecodeError):
        return jsonify({'error': 'internal server error'}), 500
