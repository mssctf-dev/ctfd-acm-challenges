from CTFd.api import CTFd_API_v1
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES


from .models import *
from .routes import cases_namespace
from .endpoints import results_namespace


def load(app):
    CTFd_API_v1.add_namespace(cases_namespace, '/cases')
    CTFd_API_v1.add_namespace(results_namespace, '/icpc_results')

    app.db.create_all()
    CHALLENGE_CLASSES["icpc_dynamic"] = DynICPCChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/ICPC_Challenges/assets/"
    )
