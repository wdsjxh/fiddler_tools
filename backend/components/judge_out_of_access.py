import time
from run import judge_out_of_access


class Judge_out_of_access:
    def __init__(self):
        self.requestdict = {}

    def run(self, requestdict):
        self.requestdict = requestdict
        judge_out_of_access(self.requestdict)
