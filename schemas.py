from CTFd.models import ma
from .models import PSubmission


class PSubmissionSchema(ma.ModelSchema):
    views = {
        'user': [
            'lang', 'status', 'result',
            'time', 'memory', 'author', 'author_team',
            'challenge_id', 'date'
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
