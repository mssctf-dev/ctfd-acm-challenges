import time

import docker
from docker.types import RestartPolicy

from ..checker import ACMAnalyzer
from ..models import PSubmission, JudgeCaseFiles


class ExecutorBase:  # (threading.Thread):
    judgers = {}

    @staticmethod
    def get_executor(task_id, lang, callback):
        return ExecutorBase.judgers[lang](task_id, callback)

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
        container = client.containers.run(
            image=image_name,
            name=container_name,
            mem_limit=limits['mem_limit'] * 2,
            mounts=[docker.types.Mount(
                type='bind',
                source=t[0],
                target=t[1],
            ) for t in binds_list.items()],
            environment=env_list,
            detach=True
        )
        for _ in range(10):
            time.sleep(wait_time // 10)
            container.reload()
            if container.status == 'exited':
                break
        if container.status == 'running':
            container.kill()
        container.remove()
        pass

    def check(self, output_dir, correct_dir, log_dir, specs):
        return self.analyzer.check(output_dir, correct_dir, log_dir, specs)

    def get_files(self):
        task = PSubmission.query.filter_by(id=self.task_id).first()
        files = JudgeCaseFiles.query.filter_by(challenge_id=task.challenge_id).all()
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

    def __init__(self, task_id, callback, *args, **kwargs):
        super(ExecutorBase, self).__init__(*args, **kwargs)
        self.task_id = task_id
        self.callback = callback
        self.analyzer = ACMAnalyzer()
