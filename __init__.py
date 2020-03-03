from CTFd.api import CTFd_API_v1
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from .api import results_namespace, cases_namespace, challenge_namespace
from .challenge import DynICPCChallenge
from .view import views


def load(app):
    CTFd_API_v1.add_namespace(cases_namespace, '/acm_chall/cases')
    CTFd_API_v1.add_namespace(results_namespace, '/acm_chall/results')
    CTFd_API_v1.add_namespace(challenge_namespace, '/acm_chall/challenge')
    app.register_blueprint(views, url_prefix='/acm_chall')

    app.db.create_all()
    CHALLENGE_CLASSES["icpc_dynamic"] = DynICPCChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/ctfd-acm-challenges/assets/"
    )
