from flask import Blueprint, send_file, Response, request, jsonify
from iturmas.decorators import login_required
from driver import control

bp = Blueprint('match', __name__)


@bp.route('/start', methods=['POST'])
@login_required(roles='admin')
def start():
    data = dict(request.form)
    try:
        control.start(**data)
    except AssertionError as e:
        return jsonify({'error': str(e)}), 400

    return Response(status=200)


@bp.route('/status')
@login_required(roles='admin')
def status():
    state = control.peek()
    return jsonify({'status': control.names[state]}), 200


@bp.route('/stop')
@login_required(roles='admin')
def stop():
    try:
        control.stop()
    except AssertionError as e:
        return jsonify({'error': str(e)}), 400

    return Response(status=200)


@bp.route('/reset')
@login_required(roles='admin')
def reset():
    try:
        control.reset()
    except AssertionError as e:
        return jsonify({'error': str(e)}), 400

    return Response(status=200)


@bp.route('/results')
@login_required(roles='admin')
def results():
    basename, fullname = control.get_result_filenames()
    try:
        return send_file(fullname, attachment_filename=basename, cache_timeout=0)
    except FileNotFoundError:
        return Response(status=404)


@bp.route('/logs')
@login_required(roles='admin')
def logs():
    basename, fullname = control.get_logs_filenames()
    try:
        return send_file(fullname, attachment_filename=basename, cache_timeout=0)
    except FileNotFoundError:
        return Response(status=404)
