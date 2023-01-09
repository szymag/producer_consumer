import threading
import logging
import queue
from src.source import Source
from src.consumer import ConsumerThread
from src.producer import ProducerThread
from src.savepicture import SavePictureThread

# Global config for logs. Uncomment if logging.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(threadName)s at %(asctime)s:  %(message)s",
)

if __name__ == "__main__":
    queue_errors = queue.Queue() # helper variable, allow for basic communication between threads
    path = "./processed/"
    frame_count = 10
    queue_a = queue.Queue(maxsize=102) # Maxsize is set to avoid memory errors in case of large dataset. 
    queue_b = queue.Queue(maxsize=102)
    
    # set and start thread that put data to queue A.
    p = ProducerThread(
        target=queue_a,
        frame_count=frame_count,
        sigkill=queue_errors,
    )
    p.start()
    # set and start thread that take data from queue A, process and put to queue B.
    c = ConsumerThread(
        target=(queue_a, queue_b),
        frame_count=frame_count,
        sigkill=queue_errors,
        kernel=1,
    )
    c.start()
    # set and start thread that take data from queue B and save to *.png file.
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
