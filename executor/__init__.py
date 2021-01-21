import os
from queue import Queue
from .base import ExecutorBase
from .cpp_executor import CppExecutor
from .python_executor import Python2Executor, Python3Executor

ExecutorBase.judgers['c'] = CppExecutor
ExecutorBase.judgers['cpp'] = CppExecutor
ExecutorBase.judgers['python2'] = Python2Executor
ExecutorBase.judgers['python3'] = Python3Executor

running = Queue(os.getenv('MAX_RUNNING') or 4)
