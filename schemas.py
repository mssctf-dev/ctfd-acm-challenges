from marshmallow import fields

from CTFd.models import ma
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.schemas.users import UserSchema
from .models import PSubmission


class PSubmissionSchema(ma.ModelSchema):
    challenge = fields.Nested(ChallengeSchema, only=['name', ])
    user = fields.Nested(UserSchema, only=['name', ])
    views = {
        'user': [
            'lang', 'status', 'result',
            'time', 'memory', 'user', 'team',
            'challenge', 'date',
        ],
        'admin': [
            'code', 'ip'
        ]
    }

    class Meta:
        model = PSubmission

    def __init__(self, view='user', *args, **kwargs):
        self.views['admin'] += self.views['user']
        kwargs['only'] = self.views[view]
        super(PSubmissionSchema, self).__init__(*args, **kwargs)
