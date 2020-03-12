from queue import Empty

from flask_apscheduler import APScheduler

from CTFd.api import CTFd_API_v1
from CTFd.plugins import (
    register_plugin_assets_directory,
    register_admin_plugin_menu_bar,
    register_user_page_menu_bar
)
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from .api import submissions_namespace, cases_namespace, challenge_namespace
from .challenge import DynICPCChallenge
from .executor import running, ExecutorBase
from .view import views


def load(app):
    CTFd_API_v1.add_namespace(cases_namespace, '/acm_chall/cases')
    CTFd_API_v1.add_namespace(submissions_namespace, '/acm_chall/submissions')
    CTFd_API_v1.add_namespace(challenge_namespace, '/acm_chall/challenge')
    app.register_blueprint(
        views, url_prefix='/acm_chall'
    )

    app.db.create_all()
    CHALLENGE_CLASSES["icpc_dynamic"] = DynICPCChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/ctfd-acm-challenges/assets/"
    )
    register_admin_plugin_menu_bar(
        'ACM Challenges', '/acm_chall/admin/judge_queue'
    )
    register_user_page_menu_bar(
        'ACM Status', '/acm_chall/judge_queue'
    )

    def poll():
        try:
            id, lang, callback = running.get(timeout=1)
            with app.app_context():
                ExecutorBase.get_executor(
                    id, lang, callback
                ).run()
        except Empty:
            pass
        except KeyboardInterrupt:
            pass

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    scheduler.add_job(id='acm-executor', func=poll, trigger="interval", seconds=10)
