from multiprocessing import Queue


locking_queue = Queue()


def lock():
    key = locking_queue.get()
    return key


def unlock():
    locking_queue.put('key')
