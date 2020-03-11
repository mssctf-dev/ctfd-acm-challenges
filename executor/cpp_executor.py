import os
import shutil

from .base import ExecutorBase
from ..models import DynICPCModel, PSubmission, db


class CppExecutor(ExecutorBase):
    def prepare_workdir(self, task):
        work_dir = os.path.join('/tmp', task.uuid)
        upload_dir = os.getenv('UPLOAD_FOLDER', None) or './CTFd/uploads'
        os.mkdir(work_dir)
        os.mkdir(os.path.join(work_dir, 'inputs'))
        os.mkdir(os.path.join(work_dir, 'outputs'))
        for i, o in self.get_files():
            shutil.copy(os.path.join(upload_dir, i.location),
                        os.path.join(work_dir, 'inputs'))
            shutil.copy(os.path.join(upload_dir, i.location),
                        os.path.join(work_dir, 'outputs'))
        os.mkdir(os.path.join(work_dir, 'compile'))
        with open(os.path.join(work_dir, 'compile', 'main.cpp'), 'w') as f:
            f.write(task.code)
        os.mkdir(os.path.join(work_dir, 'run'))
        return work_dir

    def run(self):
        work_dir = ''
        task = None
        try:
            task = PSubmission.query.filter_by(id=self.task_id).first()
            challenge = DynICPCModel.query.filter_by(id=task.challenge_id).first()
            if not challenge:
                return  # ???
            task.status = 'preparing'
            db.session.commit()
            work_dir = self.prepare_workdir(task)
            task.status = 'judging'
            db.session.commit()
            self._execute(
                'mssctf/runner_c_cpp',
                task.uuid, {
                    'mem_limit': challenge.max_memory
                }, {
                    os.path.join(work_dir, 'inputs'): '/opt/inputs',
                    os.path.join(work_dir, 'compile'): '/opt/compile',
                    os.path.join(work_dir, 'run'): '/opt/run'
                }, {
                    'TIME_LIM': challenge.max_cpu_time,
                    'MEM_LIM': challenge.max_memory,
                    'STACK_LIM': challenge.max_stack
                }, challenge.max_real_time
                if challenge.max_real_time != -1
                else challenge.max_cpu_time // 1000 * 60  # time limit in seconds * 60
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
        finally:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir, ignore_errors=True)
            if task:
                task.status = 'finishing up'
                db.session.commit()
                self.callback(task)
        pass


ExecutorBase.judgers['c'] = CppExecutor
ExecutorBase.judgers['cpp'] = CppExecutor
