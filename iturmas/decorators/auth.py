from functools import wraps
from flask import session, request, redirect, url_for, Response, flash

from models import User
from models.session import Session


def clear_session(api_route=True, next_url=''):
    next_url = next_url or request.full_path
    session.pop('email', None)
    session.pop('token', None)
    if hasattr(session, 'session_object'):
        session.session_object.remove()
        del session.session_object
    if api_route:
        return Response(status=403)
    else:
        return redirect(url_for('pages.login', next=next_url))


def login_required(roles=None, api_route=True, get_user=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'email' not in session:
                return clear_session(api_route)
            if not hasattr(session, 'session_object'):
                email = session['email']
                token = session['token']
                try:
                    s = Session.find_one(email=email, token=token)
                    if not s:
                        return clear_session(api_route)
                    if roles and s.role not in roles:
                        if api_route:
                            return Response(status=403)
                        else:
                            flash('Este usuário não está autorizado a acessar o recurso requisitado.')
                            return redirect(url_for('pages.index'))
                except ValueError:
                    return clear_session(api_route)
                session.session_object = s
                if get_user:
                    session.user = User.find_one(email=email)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
