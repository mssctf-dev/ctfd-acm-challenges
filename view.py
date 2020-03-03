from flask import Blueprint

views = Blueprint('acm_chall_views', __name__)


@views.route('/results')
def results():  # list tasks (scoreboard)
    return ''


@views.route('/admin/cases')
def cases():  # manage judge cases
    return ''


@views.route('/admin/status')
def status():  # tasks running
    return ''
