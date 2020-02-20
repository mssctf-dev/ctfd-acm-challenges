import datetime

from flask import Blueprint

from CTFd.models import db, Challenges
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

    def __init__(self, *args, **kwargs):
        super(DynICPCModel, self).__init__(**kwargs)
        self.initial = kwargs["value"]


# Better seperate from CTFd File model
# for no one want's contestants to access the test cases
class JudgeCaseFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    location = db.Column(db.Text)

    def __init__(self, challenge_id, location):
        self.challenge_id = challenge_id
        self.location = location


class ICPCSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text, default='')
    status = db.Column(db.Integer, default=1)
    result = db.Column(db.Text, default='unknown')
    time = db.Column(db.Integer, default=0)
    memory = db.Column(db.Integer, default=0)

    author = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_team = db.Column(db.Integer, db.ForeignKey("teams.id"))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
