import time
from multiprocessing.dummy import Pool
from threading import Thread

import docker

from ..models import PSubmission, JudgeCaseFiles


class JudgeThreadBase(Thread):
    judgers = {}

    @staticmethod
    def get_judger(task: PSubmission):
        return JudgeThreadBase.judgers[task.lang](task)

    @staticmethod
    def convert_readable_text(text):
        lower_text = text.lower()
        if lower_text.endswith("k"):
            return int(text[:-1]) * 1024
        if lower_text.endswith("m"):
            return int(text[:-1]) * 1024 * 1024
        if lower_text.endswith("g"):
            return int(text[:-1]) * 1024 * 1024 * 1024
        return 0

    @staticmethod
    def _execute(image_name, container_name, limits, binds_list, env_list, wait_time=10):
        client = docker.DockerClient()
        service = client.services.create(
            image=image_name,
            name=container_name,
            resources=docker.types.Resources(
                mem_limit=JudgeThreadBase.convert_readable_text(
                    limits['mem_limit']
                ) * 2,
            ),
            mounts=[docker.types.Mount(
                type='bind',
                source=t[0],
                target=t[1],
            ) for t in binds_list.items()],
            env=env_list
        )
        time.sleep(wait_time)
        service.remove()
        pass

    @staticmethod
    def judge_result(correct_dir, output_dir):
        reader = Pool(10)
        reader.map()
        pass
    
    def get_files(self):
        files = JudgeCaseFiles.query.filter_by(challenge_id=self.task.challenge_id).all()
        inputs = []
        outputs = []
        for i in files:
            if '.in' == i.location[-3:]:
                inputs.append(i)
            elif '.out' == i.location[-4:]:
                outputs.append(i)
        input_names = [i.location.split('/')[-1] for i in inputs]
        output_names = [i.location.split('/')[-1] for i in outputs]
        available_cases = [i[:i.rfind('.')]
                           for i in input_names
                           if i[:i.rfind('.')] + '.out' in output_names]
        j, k = 0, 0
        for i in range(len(available_cases)):
            while available_cases[i] + '.in' not in inputs[j].location:
                j += 1
            while available_cases[i] + '.out' not in outputs[k].location:
                k += 1
            yield inputs[j], outputs[k]

    def __init__(self, task: PSubmission):
        super(JudgeThreadBase, self).__init__()
        self.task = task
