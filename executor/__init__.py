import os
import threading
from queue import Queue, Empty
import time
from .base import JudgeThreadBase
from .cpp_executor import CppJudger

running = Queue(os.getenv('MAX_RUNNING') or 4)


def poll():
    while True:
        try:
            t = running.get(timeout=1)
            time.sleep(1)
            t.join()
        except Empty:
            pass
        except KeyboardInterrupt:
            break


threading.Thread(target=poll).start()
