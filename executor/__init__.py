import os
from queue import Queue
from .base import ExecutorBase
from .cpp_executor import CppExecutor

running = Queue(os.getenv('MAX_RUNNING') or 4)
