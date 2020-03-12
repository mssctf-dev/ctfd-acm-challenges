import datetime
import uuid

from CTFd.models import db, Challenges, Users, Teams


# from .api import *


class DynICPCModel(Challenges):  # db
    __mapper_args__ = {"polymorphic_identity": "icpc_dynamic"}
    __table_args__ = {"useexisting": True}

    id = db.Column(None, db.ForeignKey("challenges.id"), primary_key=True)

    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)

    problem_id = db.Column(db.Integer, default=-1)  # 指在评测端的id

    max_cpu_time = db.Column(db.Integer, default=1000)
    max_real_time = db.Column(db.Integer, default=-1)
    max_memory = db.Column(db.Integer, default=32 * 1024 * 1024)
    max_process_number = db.Column(db.Integer, default=200)
    max_output_size = db.Column(db.Integer, default=10000)
    max_stack = db.Column(db.Integer, default=32 * 1024 * 1024)

    dynamic_score = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        super(DynICPCModel, self).__init__(**kwargs)
        self.initial = kwargs["value"]


# Better seperate from CTFd File model
# for no one want's contestants to access the test cases
# TODO: better file management
class JudgeCaseFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    location = db.Column(db.Text)

    def __init__(self, challenge_id, location):
        self.challenge_id = challenge_id
        self.location = location


class PSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Text, default=str(uuid.uuid4()))
    code = db.Column(db.Text, default='')
    lang = db.Column(db.Text, default='')

    status = db.Column(db.Text, default='added to queue')
    result = db.Column(db.Text, default='unknown')
    time = db.Column(db.Integer, default=0)
    memory = db.Column(db.Integer, default=0)

    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    author = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_team = db.Column(db.Integer, db.ForeignKey("teams.id"))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    ip = db.Column(db.String(46))

    challenge = db.relationship(
        DynICPCModel, foreign_keys="PSubmission.challenge_id", lazy="select"
    )
    user = db.relationship(
        Users, foreign_keys="PSubmission.author", lazy="select"
    )
    team = db.relationship(
        Teams, foreign_keys="PSubmission.author_team", lazy="select"
    )

    def __init__(self, code, lang, chall_id, user_id, team_id, ip, *args, **kwargs):
        super(PSubmission, self).__init__(**kwargs)
        self.code = code
        self.lang = lang
        self.challenge_id = chall_id
        self.author = user_id
        self.author_team = team_id
        self.ip = ip
