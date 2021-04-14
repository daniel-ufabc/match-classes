from flask import Blueprint, jsonify
from models import Student, Course, Turma, CourseApplication, User
from iturmas.decorators import login_required

bp = Blueprint('stats', __name__)


@bp.route('/')
@login_required(roles='admin')
def list_stats():
    data = {
        'users': User.count(),
        'students': Student.count(),
        'courses': Course.count(),
        'classes': Turma.count(),
        'responded': CourseApplication.count()
    }

    return jsonify(data), 200
