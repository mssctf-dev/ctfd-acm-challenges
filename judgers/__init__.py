import os
import threading
from queue import Queue
import time
from .base import JudgeThreadBase
from .cpp_judger import CppJudger

running = Queue(os.getenv('MAX_RUNNING') or 4)


def poll():
    while True:
        try:
            t = running.get()
            time.sleep(1)
            t.join()
        except KeyboardInterrupt:
            break


threading.Thread(target=poll).start()
