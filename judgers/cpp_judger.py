import os
import shutil
from multiprocessing.dummy import Pool

from CTFd.models import db
from .base import JudgeThreadBase
from ..models import DynICPCModel


class CppJudger(JudgeThreadBase):
    def prepare_workdir(self):
        work_dir = os.path.join('/tmp', self.task.uuid)
        os.mkdir(work_dir)
        os.mkdir(os.path.join(work_dir, 'inputs'))
        os.mkdir(os.path.join(work_dir, 'outputs'))
        for i, o in self.get_files():
            shutil.copy(i.location, os.path.join(work_dir, 'inputs'))
            shutil.copy(o.location, os.path.join(work_dir, 'outputs'))
        os.mkdir(os.path.join(work_dir, 'compile'))
        with open(os.path.join(work_dir, 'compile', 'main.cpp'), 'w') as f:
            f.write(self.task.code)
        os.mkdir(os.path.join(work_dir, 'run'))
        return work_dir

    def run(self):
        self.task.status = 'preparing'
        db.session.commit()
        challenge = DynICPCModel.query.filter_by(id=self.task.challenge_id).first()
        if not challenge:
            return  # ???
        work_dir = ''
        try:
            work_dir = self.prepare_workdir()
            self._execute(
                'mssctf/runner_c_cpp',
                self.task.uuid, {
                    'mem_limit': challenge.max_memory
                }, {
                    os.path.join(work_dir, 'inputs'): '/opt/inputs',
                    os.path.join(work_dir, 'compile'): '/opt/compile',
                    os.path.join(work_dir, 'run'): '/opt/run'
                }, {
                    'TIME_LIM': challenge.max_cpu_time,
                    'MEM_LIM': challenge.max_memory,
                    'STACK_LIM': challenge.max_stack
                }, challenge.max_cpu_time // 500  # time limit in seconds * 2
            )
            self.judge_result(
                os.path.join(work_dir, 'run', 'outputs'),
                os.path.join(work_dir, 'outputs')
            )
        finally:
            if os.path.exists(work_dir):
                os.rmdir(work_dir)
        pass


JudgeThreadBase.judgers['c'] = CppJudger
JudgeThreadBase.judgers['cpp'] = CppJudger
