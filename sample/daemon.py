from queue import Queue
import threading
import time
import random

def basic_worker(queue, thread_name):
    while True:
        item = queue.get()
        # do_work(item)
        print("Item {} done by Thread {}".format(item, thread_name))
        queue.task_done()


def basic():
    # http://docs.python.org/library/queue.html
    queue = Queue()
    thds = []
    for i in range(3):
        t = threading.Thread(target=basic_worker, args=(queue, i), name="asek asek")
        t.daemon = True
        print("Thread {} is started".format(i))
        t.start()
        thds.append(t)
    for item in range(4):
        queue.put(item)
        print("put item: {}".format(item))
        # time.sleep( random.randint(1, 3))

    queue.join()  # block until all tasks are done
    print('got here')


basic()
