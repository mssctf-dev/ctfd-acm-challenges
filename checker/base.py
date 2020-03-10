import json
import os
from multiprocessing.dummy import Pool


class ResultAnalyzer:

    @staticmethod
    def _check_single(output_dir, correct_dir, log_dir, specs):
        reader = Pool(10)
        pref = [i.rstrip('.out') for i in os.listdir(correct_dir) if i.endswith('.out')]

        def analyze(file):
            with open(os.path.join(log_dir, file + '.log'), 'r') as f:
                log = json.loads(f.read())
            if log['exit_code'] != 0:
                return False, 'Runtime Error', log
            if log['cpu_time'] > specs['cpu_time']:
                return False, 'Time Limit Exceeded', log
            if log['memory'] > specs['memory']:
                return False, 'Memory Limit Exceeded', log

            with open(os.path.join(correct_dir, file + '.out'), 'r') as f:
                c1 = f.read().strip('\n')
            with open(os.path.join(output_dir, file + '.out'), 'r') as f:
                c2 = f.read().strip('\n')
            if c1 == c2:
                return True, 'Accepted', log
            else:
                return False, 'Wrong Answer', log

        return reader.map(analyze, pref)

    def __init__(self, *args, **kwargs):
        pass
