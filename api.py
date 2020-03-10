import datetime

from flask import (
    current_app, Blueprint, request,
    Response, stream_with_context,
    abort)
from flask_restplus import Resource, Namespace

from CTFd.models import db, Solves, Fails
from CTFd.schemas.files import FileSchema
from CTFd.utils import config, get_app_config, user
from CTFd.utils import user as current_user
from CTFd.utils.decorators import (
    authed_only, ratelimit, admins_only,
    during_ctf_time_only, require_verified_emails
)
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.uploads import get_uploader
from CTFd.utils.user import authed, get_current_team, get_current_user
from .challenge import DynICPCChallenge
# from .api import submission_list, query_details
from .models import JudgeCaseFiles, DynICPCModel, PSubmission

events = Blueprint("icpc_events", __name__)
results_namespace = Namespace("results", description='querying judge results')
judgelogs_namespace = Namespace("judge_logs", description='displaying judge logs')
cases_namespace = Namespace('cases', description='uploading and downloading judge cases')
challenge_namespace = Namespace('challenge', description='submission endpoint')


@events.route("/events")
@authed_only
@ratelimit(method="GET", limit=150, interval=60)
def subscribe():
    @stream_with_context
    def gen():
        current = user.get_current_user()
        for event in current_app.events_manager.subscribe(str(current.id)):
            yield str(event)

    enabled = get_app_config("SERVER_SENT_EVENTS")
    if enabled is False:
        return "", 204

    return Response(gen(), mimetype="text/event-stream")


@results_namespace.route('/')
class Results(Resource):
    @authed_only
    def get(self):
        pass


@judgelogs_namespace.route('/')
class JudgeLogs(Resource):
    def get(self):
        pass


@cases_namespace.route('/<int:challenge_id>')
@cases_namespace.param('challenge_id', 'challenge ID')
class ProgrammingCases(Resource):
    @admins_only
    def get(self, challenge_id):
        files = JudgeCaseFiles.query.filter_by(challenge_id=challenge_id).all()
        schema = FileSchema(many=True)
        response = schema.dump(files)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def post(self, challenge_id):
        files = request.files.getlist("file")
        objs = []
        for f in files:
            if not f.filename or len(f.filename) == 0:
                continue
            uploader = get_uploader()
            location = uploader.upload(file_obj=f, filename=f.filename)
            file_row = JudgeCaseFiles(
                challenge_id=challenge_id, location=location
            )
            db.session.add(file_row)
            objs.append(file_row)
        db.session.commit()
        schema = FileSchema(many=True)
        response = schema.dump(objs)
        if response.errors:
            return {"success": False, "errors": response.errorss}, 400
        return {"success": True, "data": response.data}

    @admins_only
    def delete(self, challenge_id):
        uploader = get_uploader()
        files = JudgeCaseFiles.query.filter_by(challenge_id=challenge_id).all()
        for f in files:
            uploader.delete(f.location)
        JudgeCaseFiles.query.filter_by(challenge_id=challenge_id).delete()
        db.session.commit()
        db.session.close()


@challenge_namespace.route('/attempt')
class Challenge(Resource):
    @check_challenge_visibility
    @during_ctf_time_only
    @require_verified_emails
    def post(self):
        if authed() is False:
            return {"success": True, "data": {"status": "authentication_required"}}, 403
        if request.content_type != "application/json":
            request_data = request.form
        else:
            request_data = request.get_json()
        challenge_id = request_data.get("challenge_id")
        challenge = DynICPCModel.query.filter_by(id=challenge_id).first_or_404()
        user = get_current_user()
        team = get_current_team()
        if current_user.is_admin():
            preview = request.args.get("preview", False)
            if preview:
                status, message = DynICPCChallenge.real_attempt(user, team, challenge, request)

                return {
                    "success": True,
                    "data": {
                        "status": "already_solved" if status else "incorrect",
                        "message": message,
                    },
                }
        if (config.is_teams_mode() and team is None) or (challenge.state == "locked"):
            abort(403)
        if challenge.state == "hidden":
            abort(404)

        if challenge.requirements:
            requirements = challenge.requirements.get("prerequisites", [])
            solve_ids = (
                Solves.query.with_entities(Solves.challenge_id)
                    .filter_by(account_id=user.account_id)
                    .order_by(Solves.challenge_id.asc())
                    .all()
            )
            solve_ids = set([solve_id for solve_id, in solve_ids])
            prereqs = set(requirements)
            if solve_ids < prereqs:
                abort(403)

        ten_sec_ago = datetime.datetime.utcnow() + datetime.timedelta(seconds=-10)

        if PSubmission.query.filter(PSubmission.date >= ten_sec_ago).first():
            return (
                {
                    "success": True,
                    "data": {
                        "status": "ratelimited",
                        "message": "You're submitting too fast. Slow down.",
                    },
                },
                429,
            )

        solves = Solves.query.filter_by(
            account_id=user.account_id, challenge_id=challenge_id
        ).first()
        fails = Fails.query.filter_by(
            account_id=user.account_id, challenge_id=challenge_id
        ).count()
        if not solves:
            max_tries = challenge.max_attempts
            if max_tries and fails >= max_tries > 0:
                return (
                    {
                        "success": True,
                        "data": {
                            "status": "incorrect",
                            "message": "You have 0 tries remaining",
                        },
                    },
                    403,
                )
        else:
            return {
                "success": True,
                "data": {
                    "status": "already_solved",
                    "message": "You already solved this",
                },
            }

        status, message = DynICPCChallenge.real_attempt(user, team, challenge, request)

        return {
            "success": True,
            "data": {
                "status": "already_solved" if status else "incorrect",
                "message": message,
            },
        }
