import os

sem = None

def init():
    global sem
    sem = os.Semaphore()

def wait(timeout:int) -> int:
    global sem
    return sem.wait(timeout)

def signal():
    global sem
    sem.signal()
