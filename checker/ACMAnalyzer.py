from .base import ResultAnalyzer


class ACMAnalyzer(ResultAnalyzer):
    def check(self, output_dir, correct_dir, log_dir, specs):
        res = self._check_single(output_dir, correct_dir, log_dir, specs)
        if len(res) == 0:
            return 'Not Enabled Yet', {}
        final = res[0][2]
        for i in res:
            if not i[0]:
                return i[1], i[2]
            else:
                for k in i[2].keys():
                    if i[2][k] > final[k]:
                        final[k] = i[2][k]

        return 'Accepted', final

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
