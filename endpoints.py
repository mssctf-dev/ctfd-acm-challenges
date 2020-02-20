import json

from flask import (
    current_app, Blueprint,
    Response, stream_with_context,
    render_template_string,
    Namespace, request
)
from flask_restplus import Resource

from CTFd.utils import get_app_config
from CTFd.utils.decorators import authed_only, ratelimit, admins_only
from CTFd.utils.uploads import get_uploader
from CTFd.utils import user
from CTFd.schemas.files import FileSchema
from CTFd.models import db, Submissions, Users

# from .api import submission_list, query_details
from .models import JudgeCaseFiles

events = Blueprint("icpc_events", __name__)
results_namespace = Namespace("results", description='querying judge results')
judgelogs_namespace = Namespace("judge_logs", description='displaying judge logs')
cases_namespace = Namespace('cases', description='uploading and downloading judge cases')

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
        return ("", 204)

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
            uploader = get_uploader()
            location = uploader.upload(file_obj=f, filename=f.filename)
            file_row = JudgeCaseFiles(
                challenge_id=challenge_id, location=location
            )
            db.session.add(file_row)
            db.session.commit()
            objs.append(file_row)
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
