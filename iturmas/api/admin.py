from flask import Blueprint, request, jsonify, Response
from werkzeug.security import check_password_hash

import config
from iturmas.decorators import login_required
from models import mapping
from dependencies.mariadb import db


bp = Blueprint('admin', __name__)


@bp.route('/table/<domain>', methods=['DELETE'])
@login_required(roles='admin')
def clear_table(domain):
    if domain not in mapping and domain != 'preferences':
        return jsonify({'error': 'Invalid domain.'}), 400
    data = request.json
    if 'password' not in data:
        return jsonify({'error': 'missing password field'}), 400
    password = data['password']
    if check_password_hash(config.DATABASE_CLEAR_PASSWORD_HASH, password):
        if not db:
            return jsonify({'error': 'database not connected'}), 500
        if domain != 'preferences':
            db.query(f'TRUNCATE TABLE {domain};')
        else:
            db.query(f'TRUNCATE TABLE class_applications;')
            db.query(f'TRUNCATE TABLE course_applications;')

        return Response(status=200)
    return Response(status=403)


@bp.route('/database', methods=['DELETE'])
@login_required(roles='admin')
def clear_db():
    data = request.json
    if 'password' not in data:
        return jsonify({'error': 'missing password field'}), 400
    password = data['password']
    if check_password_hash(config.DATABASE_CLEAR_PASSWORD_HASH, password):
        if not db:
            return jsonify({'error': 'database not connected'}), 500
        db.reset()

        return Response(status=200)
    return Response(status=403)
