from queue import Queue
from threading import Thread
from .gen_pdf import CreatePdfTask, create_pdf


class TaskWorker(Thread):
    def __init__(self, queue: Queue):
        super().__init__(daemon=True)
        self.queue = queue

    @classmethod
    def run_forever(cls, max_queue_size: int = 100) -> "TaskWorker":
        self = cls(Queue(max_queue_size))
        self.start()
        return self

    def run(self):
        while True:
            task: CreatePdfTask = self.queue.get()
            create_pdf(task)
