import os

from redis.exceptions import RedisError
from flask import Blueprint, request, Response, jsonify, send_file
from werkzeug.security import check_password_hash

import config
from dependencies.queue import redis_queue
from iturmas.decorators.auth import login_required

from models import mapping
from tasks.data import import_data, export_data
from utils.files import data_filename, upload_filename, generate_upload_basename

bp = Blueprint('batch', __name__)


@bp.route('/request/<domain>')
@login_required(roles='admin')
def request_download(domain):
    if domain not in mapping and domain != 'preferences':
        return Response(status=404)

    job = redis_queue.enqueue(export_data, domain, result_ttl=3600)
    return jsonify({'job_id': job.get_id()}), 200


@bp.route('/download/<link>')
@login_required(roles='admin')
def download(link):
    fullname = data_filename(link)
    if '/' in link or not os.path.exists(fullname):
        return Response(status=404)
    return send_file(fullname, cache_timeout=0)


@bp.route('/check/<link>')
@login_required(roles='admin')
def check(link):
    fullname = data_filename(link)
    if '/' in link or not os.path.exists(fullname):
        return Response(status=404)
    return Response(status=200)


@bp.route('/upload/<domain>', methods=['POST'])
@login_required(roles='admin')
def upload(domain):
    if domain not in mapping:
        return jsonify({'error': 'Invalid domain.'}), 400
    if 'file' not in request.files:
        return jsonify({'error': 'No file part.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    filename = upload_filename(generate_upload_basename(file.filename))
    file.save(filename)

    update = bool(request.form.get('update', False))
    job = redis_queue.enqueue(import_data, domain, filename, update, result_ttl=3600)
    return jsonify({'job_id': job.get_id()}), 200


@bp.route('/upload_preferences', methods=['POST'])
@login_required(roles='admin')
def upload_preferences():
    if 'password' not in request.form:
        return jsonify({'error': 'missing password field'}), 400
    password = request.form['password']
    if not check_password_hash(config.DATABASE_CLEAR_PASSWORD_HASH, password):
        return Response(status=403)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    filename = upload_filename(generate_upload_basename(file.filename))
    file.save(filename)

    job = redis_queue.enqueue(import_data, 'preferences', filename, True, result_ttl=3600)
    return jsonify({'job_id': job.get_id()}), 200


@bp.route('/job_status/<job_id>')
@login_required(roles='admin')
def status(job_id):
    try:
        job = redis_queue.fetch_job(job_id)
        if not job:
            return Response(status=404)
        response = {'status': job.get_status(refresh=True)}
        if job.is_finished:
            # jobs can set 'status' to "failed" and 'error' to the appropriate msg in job.result
            #     if they want to indicate a failure in the process (without actually raising an error).
            response.update(job.result)
        elif job.is_failed:
            response['error'] = str(job.exc_info)
    except RedisError:
        response = {'status': 'unknown', 'info': 'could not connect to job queue.'}

    return jsonify(response), 200
