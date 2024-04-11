import time
from threading import Timer
from PyQt5.QtCore import QObject, QEvent
from multiprocessing import shared_memory
from contextlib import contextmanager

class Debouncer:
    def __init__(self, fn, time, non_debounced=lambda: None) -> None:
        self.fn = fn
        self.time = time
        self.last_time = 0
        self.finished = True
        self.non_debounced = non_debounced

    def cal(self):
        time_now = time.time()
        print("cal called", time_now, time.time())
        self.non_debounced()
        if time_now - self.last_time > self.time:

            def execute():
                if self.finished:
                    try:
                        self.finished = False
                        self.last_time = time_now
                        self.fn()
                    finally:
                        self.finished = True
                        print("finished", time_now, time.time())
                    
            if self.finished:
                execute()
                return

            t = Timer(self.time, execute)
            t.start()


class ColorButtonFilter(QObject):
    def __init__(self, function,wheel_handler=None):
        super().__init__()
        self.function = function
        self.wheel_handler = wheel_handler 

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.function:
                self.function()
            return True
        if event.type() == QEvent.Wheel:
            print(event.angleDelta())
            if self.wheel_handler:
                self.wheel_handler(event.angleDelta())
        return super().eventFilter(obj, event)

@contextmanager
def shared_memory_context(name: str, size: int, destroy: bool, create=bool):
    shm = None
    if size is None:
        shm = shared_memory.SharedMemory(name=name, create=create)
    else:
        shm = shared_memory.SharedMemory(name=name, create=create, size=size)

    try:
        yield shm
    finally:
        if destroy:
            shm.unlink()
        else:
            shm.close()

def check_shared_memory_exists(name):
    try:
        shm = shared_memory.SharedMemory(name=name)
        shm.close()
        return True
    except FileNotFoundError:
        return False
