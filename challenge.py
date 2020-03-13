import math
import uuid
from base64 import b64decode
from queue import Full

from flask import Blueprint

from CTFd.models import (
    db, Challenges, ChallengeFiles, Tags, Flags, Solves, Hints, Fails,
    Users, Teams)
from CTFd.plugins.challenges import BaseChallenge
from CTFd.utils.modes import get_model
from CTFd.utils.uploads import delete_file, get_uploader
from CTFd.utils.user import get_ip
from .executor import running
from .models import DynICPCModel, JudgeCaseFiles, PSubmission


class DynICPCChallenge(BaseChallenge):
    id = "icpc_dynamic"
    name = "icpc_dynamic"
    route = "/plugins/ctfd-acm-challenges/assets/"
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/ctfd-acm-challenges/assets/html/create.html",
        "update": "/plugins/ctfd-acm-challenges/assets/html/update.html",
        "view": "/plugins/ctfd-acm-challenges/assets/html/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/ctfd-acm-challenges/assets/js/create.js",
        "update": "/plugins/ctfd-acm-challenges/assets/js/update.js",
        "view": "/plugins/ctfd-acm-challenges/assets/js/view.js",
    }
    blueprint = Blueprint(
        "ctfd-acm-challenges",
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
            'dynamic_score': challenge.dynamic_score,
        }

    @staticmethod
    def update(challenge, request):
        data = request.form or request.get_json()

        for attr, value in data.items():
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            if attr in [
                'id', 'name', 'value', 'description', 'category', 'state', 'max_attempts', 'type', 'type_data',
                'dynamic_score',
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
    def post_process(task: PSubmission):
        challenge = DynICPCModel.query.filter_by(id=task.challenge_id).first()
        user = Users.query.filter_by(id=task.author).first()
        team = Teams.query.filter_by(id=task.author_team).first()
        if task.result == 'Accepted':
            DynICPCChallenge.real_solve(user, team, challenge, task)
        else:
            DynICPCChallenge.real_fail(user, team, challenge, task)
        pass

    @staticmethod
    def attempt(chall, req):
        return False, 'Invalid Operation'

    @staticmethod
    def real_attempt(user, team, challenge, request):
        r = request.form or request.get_json()
        try:
            r['code'] = b64decode(r['submission']).decode()
            task = PSubmission(
                code=r['code'],
                lang=r['language'],
                chall_id=challenge.id,
                user_id=user.id,
                team_id=team.id if team else None,
                ip=get_ip(req=request),
                uuid=str(uuid.uuid1()),
            )
            db.session.add(task)
            db.session.commit()

            while True:
                try:
                    running.put((task.id, task.lang,
                                 DynICPCChallenge.post_process))
                    break
                except Full:
                    pass  # warning: timeout, trying again
        except Exception as e:
            import logging
            logging.exception(e)
            return False, 'error'
        return True, 'Added to Judge Queue'

    @staticmethod
    def fail(user, team, chall, req):
        pass

    @staticmethod
    def real_fail(user, team, challenge, task):
        db.session.add(Fails(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=task.ip,
            provided=task.id
        ))
        db.session.commit()
        db.session.close()

    @staticmethod
    def solve(user, team, challenge, request):
        pass

    @staticmethod
    def real_solve(user, team, challenge, task):
        chal = DynICPCModel.query.filter_by(id=challenge.id).first()

        db.session.add(Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=task.ip,
            provided=task.id
        ))

        Model = get_model()
        solve_count = (
            Solves.query.join(Model, Solves.account_id == Model.id).filter(
                Solves.challenge_id == challenge.id,
                Model.hidden == False,
                Model.banned == False,
            ).count()
        )

        # We subtract -1 to allow the first solver to get max point value
        solve_count -= 1
        if chal.dynamic_score:
            value = (((chal.minimum - chal.initial) / (chal.decay ** 2))
                     * (solve_count ** 2)) + chal.initial
            value = math.ceil(value)
            if value < chal.minimum:
                value = chal.minimum
        else:
            value = chal.initial

        chal.value = value
        db.session.commit()
        db.session.close()
