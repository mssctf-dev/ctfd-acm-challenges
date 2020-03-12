from flask import Blueprint, render_template

from CTFd.models import Solves, Challenges
from CTFd.utils.decorators import admins_only, authed_only
from .models import DynICPCModel, PSubmission

views = Blueprint('acm_chall_views', __name__,
                  template_folder='templates', )


@views.route('/board')
@authed_only
def scoreboard():  # list tasks (scoreboard)
    challenges = DynICPCModel.query.all()

    return render_template('board.html', admin=False, challenges=challenges)


@views.route('/judge_queue')
@authed_only
def queue():
    PSubmission.query.all()
    return render_template('judge_queue.html', admin=False)


@views.route('/admin/board')
@authed_only
@admins_only
def admin_scoreboard():  # tasks running
    return render_template('board.html', admin=True)


@views.route('/admin/judge_queue')
@authed_only
@admins_only
def admin_queue():
    return render_template('judge_queue.html', admin=True)


@views.route('/admin/cases')
@authed_only
@admins_only
def cases():  # manage judge cases
    return render_template('case.html')
