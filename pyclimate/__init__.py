import os
import multiprocessing

class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison Pill says exit
                print('%s: Exiting' % proc_name)
                break
            print('{}: {}'.format(proc_name, next_task))
            answer = next_task()
            self.result_queue.put(answer)
        return
