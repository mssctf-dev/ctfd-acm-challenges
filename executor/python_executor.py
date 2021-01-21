import json
import os
import shutil

from .base import ExecutorBase
from ..models import DynICPCModel, PSubmission, db


class PythonExecutor(ExecutorBase):
    lang = ''
    def prepare_workdir(self, task):
        work_dir = os.path.join('/tmp', task.uuid)
        upload_dir = os.getenv('UPLOAD_FOLDER', None) or './CTFd/uploads'
        os.mkdir(work_dir)
        os.mkdir(os.path.join(work_dir, 'inputs'))
        os.mkdir(os.path.join(work_dir, 'outputs'))
        for i, o in self.get_files():
            shutil.copy(os.path.join(upload_dir, i.location),
                        os.path.join(work_dir, 'inputs'))
            shutil.copy(os.path.join(upload_dir, o.location),
                        os.path.join(work_dir, 'outputs'))
        os.mkdir(os.path.join(work_dir, 'run'))
        with open(os.path.join(work_dir, 'run', 'main.py'), 'w') as f:
            f.write(task.code)
        return work_dir

    def run(self):
        try:
            task = PSubmission.query.filter_by(id=self.task_id).first()
            challenge = DynICPCModel.query.filter_by(
                id=task.challenge_id).first()
            work_dir = self.prepare_workdir(task)
            task.status = 'judging'
            db.session.commit()
            self._execute(
                'mssctf/runner_'+self.lang,
                task.uuid, {
                    'mem_limit': challenge.max_memory * 8
                }, {
                    os.path.join(work_dir, 'inputs'): '/opt/inputs',
                    os.path.join(work_dir, 'run'): '/opt/run'
                }, {
                    'TIME_LIM': challenge.max_cpu_time * 4,
                    'MEM_LIM': challenge.max_memory * 4,
                    # 'STACK_LIM': challenge.max_stack
                }, challenge.max_real_time * 3
                if challenge.max_real_time != -1
                else challenge.max_cpu_time // 1000 * 60 * 2  # time limit in seconds * 60
            )
            result, stats = self.check(
                os.path.join(work_dir, 'run', 'outputs'),
                os.path.join(work_dir, 'outputs'),
                os.path.join(work_dir, 'run', 'outputs'), {
                    'cpu_time': challenge.max_cpu_time,
                    'memory': challenge.max_memory,
                    # 'STACK_LIM': challenge.max_stack
                }
            )
            task.result = result
            task.time = stats['cpu_time']
            task.memory = stats['memory']
            db.session.commit()
        except Exception as e:
            print(e)
        finally:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir, ignore_errors=True)
            if task:
                task.status = 'finished'
                db.session.commit()
                self.callback(task)
        pass

class Python2Executor(PythonExecutor):
    lang = 'python2'
class Python3Executor(PythonExecutor):
    lang = 'python3'
