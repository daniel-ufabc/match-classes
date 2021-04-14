import os

from flask import Blueprint, render_template, session, redirect, jsonify, url_for, flash, request
from werkzeug.security import generate_password_hash
import markdown as md

import config
from iturmas.decorators import login_required
from iturmas.api import auth
from driver.control import peek, CLEAN, RUNNING, SUCCESS, FAILURE, ZOMBIE, get_progress
from driver.extract import get_courses_and_classes_data, get_parameters
from iturmas.decorators.auth import clear_session
from models import Student, Course, Turma, CourseApplication, User

bp = Blueprint('pages', __name__)


@bp.route('/reset_password/<token>')
def reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('pages.login', messages=['O link para definição de senha não é válido.']))
    return render_template('reset_password.html', token=token)


@bp.route('/define_new_password')
def define_new_password():
    return render_template('define_new_password.html')


@bp.route('/request_define_password')
def request_define_password():
    response, code = auth.request_define_password()
    if code == 400:
        flash('O email não está registrado em nossas bases de dados.')
    else:
        flash('Você receberá um e-mail em instantes com instruções para definir nova senha.')
    return render_template('login.html')


@bp.route('/set_password', methods=['POST'])
def set_password():
    try:
        token = request.form['reset_password_token']
        password1 = request.form['password1']
        password2 = request.form['password2']
        assert password1 == password2
    except KeyError:
        # This should not happen if user "used" served form
        return redirect(url_for('pages.login'))

    user = User.verify_reset_password_token(token)
    if not user:
        # TODO: check this actually goes to the login page...
        flash('O link para definição de senha não é válido.')
        return redirect(url_for('pages.login'))

    user.password = generate_password_hash(password1, salt_length=16)
    user.save(on_duplicate_key_update=True)

    # TODO: check this actually goes to the login page...
    flash('Nova senha definida com sucesso! Tente fazer login.')
    return redirect(url_for('pages.login'))


@bp.route('/<domain>/index')
@login_required(roles='admin', api_route=False)
def generic_index(domain):
    if domain not in ['classes', 'courses', 'students']:
        return jsonify({'error': 'Invalid domain.'}), 400
    return render_template(domain + '.html')


@bp.route('/')
@login_required(api_route=False)
def index():
    print(session.session_object.role)
    if session.session_object.role == 'admin':
        return redirect('/panel')
    return redirect('/pref/main')


@bp.route('/login')
def login():
    return render_template('login.html')


@bp.route('/help')
def app_help():
    try:
        with open('../README.md') as f:
            html = md.markdown(f.read())
    except IOError:
        flash('Help não foi encontrado, por favor contacte o administrador.')
        return redirect(url_for('pages.index'))

    return render_template('help.html', html_content=html)


@bp.route('/logout')
def logout():
    clear_session()
    return redirect(url_for('pages.login', next=''))


# noinspection PyBroadException
@bp.route('/panel')
@login_required(roles='admin', api_route=False)
def panel():
    try:
        _1, _2, criteria_list = get_courses_and_classes_data()
    except:
        criteria_list = ['Error in driver: could not fetch list of criteria.']
    return render_template(
        'panel.html',
        default_max_search=config.DEFAULT_MAX_SEARCH,
        parameters=get_parameters(criteria_list)
    )


@bp.route('/list_stats')
@login_required(roles='admin', api_route=False)
def list_stats():
    data = {
        'users': User.count(),
        'students': Student.count(),
        'courses': Course.count(),
        'classes': Turma.count(),
        'responded': CourseApplication.count()
    }

    return render_template('status.html', data=data)


@bp.route('/list_runs')
@login_required(roles='admin', api_route=False)
def list_runs():
    state = peek()
    info = {
        CLEAN: 'Não iniciado.',
        RUNNING: 'Em execução.',
        SUCCESS: 'Concluído com sucesso.',
        FAILURE: 'Concluído com erro.',
        ZOMBIE: 'Interrompido com erro.'
    }

    progress = get_progress()
    print(state)
    print(progress)

    return render_template('execution.html', state=state, status=info[state], progress=progress)

