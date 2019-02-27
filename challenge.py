import math
from base64 import b64decode

from flask import Blueprint

from CTFd.models import (
    db, Challenges, ChallengeFiles, Tags, Flags, Solves, Hints, Fails
)
from CTFd.plugins.challenges import BaseChallenge
from CTFd.utils.modes import get_model
from CTFd.utils.uploads import delete_file, get_uploader
from CTFd.utils.user import get_ip
from .models import DynICPCModel, JudgeCaseFiles


class DynICPCChallenge(BaseChallenge):
    id = "icpc_dynamic"
    name = "icpc_dynamic"
    route = "/plugins/ICPC_Challenges/assets/"
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/ICPC_Challenges/assets/create.html",
        "update": "/plugins/ICPC_Challenges/assets/update.html",
        "view": "/plugins/ICPC_Challenges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/ICPC_Challenges/assets/create.js",
        "update": "/plugins/ICPC_Challenges/assets/update.js",
        "view": "/plugins/ICPC_Challenges/assets/view.js",
    }
    blueprint = Blueprint(
        "ICPC_Challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )

    @staticmethod
    def create(request):
        data = request.form or request.get_json()
        challenge = DynICPCModel(**data)

        db.session.add(challenge)
        db.session.commit()

        return challenge

    @staticmethod
    def read(challenge):
        challenge = DynICPCModel.query.filter_by(id=challenge.id).first()
        return {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "initial": challenge.initial,
            "decay": challenge.decay,
            "minimum": challenge.minimum,
            "description": challenge.description,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": DynICPCChallenge.id,
                "name": DynICPCChallenge.name,
                "templates": DynICPCChallenge.templates,
                "scripts": DynICPCChallenge.scripts,
            },
            'max_cpu_time': challenge.max_cpu_time,
            'max_real_time': challenge.max_real_time,
            'max_memory': challenge.max_memory,
            'max_process_number': challenge.max_process_number,
            'max_output_size': challenge.max_output_size,
            'max_stack': challenge.max_stack,
        }

    @staticmethod
    def update(challenge, request):
        data = request.form or request.get_json()

        for attr, value in data.items():
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            if attr in [
                'id', 'name', 'value', 'description', 'category', 'state', 'max_attempts', 'type', 'type_data',

                'max_cpu_time', 'max_real_time', 'max_memory', 'max_process_number', 'max_output_size', 'max_stack'
            ]:
                setattr(challenge, attr, value)

        Model = get_model()

        solve_count = (
            Solves.query.join(Model, Solves.account_id == Model.id).filter(
                Solves.challenge_id == challenge.id,
                Model.hidden == False,
                Model.banned == False,
            ).count()
        )

        # It is important that this calculation takes into account floats.
        # Hence this file uses from __future__ import division
        value = (((challenge.minimum - challenge.initial) / (challenge.decay ** 2))
                 * (solve_count ** 2)) + challenge.initial

        value = math.ceil(value)

        if value < challenge.minimum:
            value = challenge.minimum

        challenge.value = value

        db.session.commit()
        return challenge

    @staticmethod
    def delete(challenge):
        Fails.query.filter_by(challenge_id=challenge.id).delete()
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        Flags.query.filter_by(challenge_id=challenge.id).delete()

        files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
        for f in files:
            delete_file(f.id)
        ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
        uploader = get_uploader()
        files = JudgeCaseFiles.query.filter_by(challenge_id=challenge.id).all()
        for f in files:
            uploader.delete(f.location)
        JudgeCaseFiles.query.filter_by(challenge_id=challenge.id).delete()

        Tags.query.filter_by(challenge_id=challenge.id).delete()
        Hints.query.filter_by(challenge_id=challenge.id).delete()
        DynICPCModel.query.filter_by(id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @staticmethod
    def attempt(challenge, request):
        r = request.form or request.get_json()
        r['code'] = b64decode(r['submission']).decode()
        prepare_challenge(challenge)
        pid = DynICPCModel.query.filter(
            DynICPCModel.id == challenge.id).first().problem_id
        content = request_judge(pid, r['code'], r['language'])
        request.judge_result = content
        if content['result'] != 0:
            return False, content['message']
        else:
            return True, 'Accepted'

    @staticmethod
    def fail(user, team, challenge, request):
        db.session.add(Fails(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(request),
            provided=request.judge_result['submission_id']
        ))
        db.session.commit()
        db.session.close()

    @staticmethod
    def solve(user, team, challenge, request):
        chal = DynICPCModel.query.filter_by(id=challenge.id).first()
        Model = get_model()
        solve = Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(request),
            provided=request.judge_result['submission_id']
        )
        db.session.add(solve)
        solve_count = (
            Solves.query.join(Model, Solves.account_id == Model.id).filter(
                Solves.challenge_id == challenge.id,
                Model.hidden == False,
                Model.banned == False,
            ).count()
        )

        # We subtract -1 to allow the first solver to get max point value
        solve_count -= 1

        value = (((chal.minimum - chal.initial) / (chal.decay ** 2))
                 * (solve_count ** 2)) + chal.initial

        value = math.ceil(value)
        if value < chal.minimum:
            value = chal.minimum

        chal.value = value
        db.session.commit()
        db.session.close()
