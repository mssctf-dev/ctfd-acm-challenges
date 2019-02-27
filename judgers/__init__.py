import os
from queue import Queue, Full
from threading import Thread

from .base import JudgeThreadBase


class JudgeQueue(Queue, Thread):  # item: task

    def __init__(self):
        super(JudgeQueue, self).__init__()
        self.running = Queue(os.getenv('MAX_RUNNING') or 4)

    def run(self):
        while True:
            task = self.get()
            thread = JudgeThreadBase.get_judger(task)
            while True:
                try:
                    self.running.put(thread, timeout=10)
                    thread.start()
                    break
                except Full:
                    pass  # warning: timeout, trying again
