from flask import Blueprint, render_template
from CTFd.utils.decorators import admins_only

views = Blueprint('acm_chall_views', __name__,
                  template_folder='templates', )


@views.route('/status')
def results():  # list tasks (scoreboard)

    return render_template('status.html', admin=False)


@views.route('/admin/cases')
@admins_only
def cases():  # manage judge cases
    return ''


@views.route('/admin/status')
@admins_only
def status():  # tasks running
    return render_template('status.html', admin=True)
