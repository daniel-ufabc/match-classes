import pymysql
from flask import Blueprint, jsonify, session, Response, request, render_template

import config
from iturmas.decorators import login_required
from models import mapping

bp = Blueprint('search', __name__)


@bp.route('/<domain>')
@login_required(roles=['student', 'admin'])
def find(domain):
    if domain not in config.CRUD_DOMAINS:
        return jsonify({'error': 'invalid domain'}), 400
    se = session.session_object
    if se.role != 'admin' and domain not in ['courses', 'classes']:
        return Response(status=403)

    try:
        search_string = request.args['search_string']
        limit = request.args['limit']
        offset = request.args['offset']
    except KeyError as e:
        return jsonify({'error': 'missing required field', 'details': str(e)}), 400

    try:
        cls = mapping[domain]
        total = cls.count(search_string=search_string)
        records = cls.search(search_string=search_string, limit_offset=(limit, offset))
        formatted_records = [{key: record[i] for i, key in enumerate(cls.column_names)} for record in records]
        print(formatted_records[0] if formatted_records else 'No record to print.')
        html_entries = render_template(f'{domain}_range.html', records=formatted_records)

        return jsonify({
            'entries': html_entries,
            'records': records,
            'total': total,
            'offset': offset,
            'limit': limit,
        }), 200
    except pymysql.err.Error as e:
        print('$' * 50)
        print(e)
        return Response(status=500)


@bp.route('/count/<domain>')
@login_required(roles=['student', 'admin'])
def count(domain):
    if domain not in mapping:
        return jsonify({'error': 'invalid domain'}), 400
    se = session.session_object
    if se.role != 'admin' and domain not in ['classes', 'courses']:
        return Response(status=403)

    search_string = request.args.get('search_string', '')
    try:
        cls = mapping[domain]
        res = cls.count(search_string=search_string)
        return jsonify({'count': res}), 200
    except pymysql.err.Error:
        return Response(status=500)


@bp.route('/autocomplete/<domain>')
@login_required(roles='admin')
def autocomplete(domain):
    if domain not in mapping:
        return jsonify({'error': 'invalid domain'}), 400
    se = session.session_object
    if se.role != 'admin' and domain not in ['courses', 'classes']:
        return Response(status=403)
    try:
        search_string = request.args['term']
    except KeyError as e:
        return jsonify({'error': 'missing required field', 'details': str(e)}), 400

    try:
        cls = mapping[domain]
        records = cls.search(search_string=search_string, limit_offset=(10, 0))
    except pymysql.err.Error as e:
        print('$' * 50, 'DEBUG', '$' * 50)
        print(e)
        return Response(status=500)

    response = [{'label': str(record[0]).rjust(16) + ' -- ' + record[1], 'value': record[0]} for record in records]

    return jsonify(response), 200
