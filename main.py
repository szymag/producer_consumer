import threading
import os
import sys
import logging
import queue
from src.source import Source
from src.consumer import ConsumerThread
from src.producer import ProducerThread
from src.savepicture import SavePictureThread

# uncomment if logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(threadName)s at %(asctime)s:  %(message)s",
)

if __name__ == "__main__":
    queue_errors = queue.Queue()
    path = "./processed/"
    queue_a = queue.Queue(maxsize=102)
    queue_b = queue.Queue(maxsize=102)
    frame_count = 100

    p = ProducerThread(
        target=queue_a,
        frame_count=frame_count,
        sigkill=queue_errors,
    )
    p.start()

    c = ConsumerThread(
        target=(queue_a, queue_b),
        frame_count=frame_count,
        sigkill=queue_errors,
        kernel=1,
    )
    c.start()
    c1 = SavePictureThread(
        target=queue_b,
        frame_count=frame_count,
        path=path,
        sigkill=queue_errors,
    )
    c1.start()
    p.join()
    c.join()
    c1.join()
    logging.debug("finished")
