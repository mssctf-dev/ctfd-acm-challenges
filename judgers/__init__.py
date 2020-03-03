import os
from queue import Queue, Full
from threading import Thread

from .base import JudgeThreadBase


class JudgeQueue(Thread, Queue):  # item: task

    def __init__(self):
        Thread.__init__(self)
        Queue.__init__(self)
        self.running = Queue(os.getenv('MAX_RUNNING') or 4)

    def run(self):
        while True:
            try:
                task_id, callback = self.get()
                # assert type(task) == PSubmission
                thread = JudgeThreadBase.get_judger(task_id, callback)
                while True:
                    try:
                        self.running.put(thread, timeout=10)
                        thread.start()
                        break
                    except Full:
                        pass  # warning: timeout, trying again
            except KeyboardInterrupt:
                break
            except Exception as e:
                import logging
                logging.exception(e)


queue = JudgeQueue()
queue.start()
