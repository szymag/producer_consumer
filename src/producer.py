import threading
import queue
import logging
import sys
import time
import numpy as np
from src.source import Source


class ProducerThread(threading.Thread):
    def __init__(
        self,
        target: queue,
        sigkill: queue,
        name: str = "Producer",
        frame_count: int = 100,
        picture_shape: (int, int) = (768, 1024),
    ):
        """A thread that is responsible for retriving data from Source
        and pass them to queue that is shared with Consumer.

        Args:
            target (queue): queue share data between threads.
            sigkill (queue): queue that is shared between all the threads.
            It keeps track whether any of them is interrupted.
            In such case, the rest should be stopped.
            name (str, optional): Name of the thread. Defaults to Producer.
            frame_count (int, optional): How many times data are taken from Source.
            Defaults to 100.
            picture_shape (tuple, optional): Dimensions of pictures. Defaults to (768, 1024).

        """
        super(ProducerThread, self).__init__()
        self.target = target
        assert isinstance(self.target, queue.Queue)
        self.sigkill = sigkill
        assert isinstance(self.sigkill, queue.Queue)
        self.name = name
        self.frame_count = frame_count
        assert (isinstance(self.frame_count, int) and self.frame_count > 0
        ), "Number of data must be natural number bigger than 0"
        self.picture_shape = picture_shape
        assert (
            self.picture_shape[0] > 0
            and self.picture_shape[1] > 0
            and isinstance(self.picture_shape[0], int)
            and isinstance(self.picture_shape[1], int)
        ), "Dimensions of picture must be natural numer bigger than 0"
        self.source = Source((*picture_shape, 3))
        self.delay_frame = 0.05
        return

    def run(self):
        for i in range(self.frame_count):
            try:
                item = self.source.get_data()
                self.target.put(item)
                time.sleep(self.delay_frame)
                logging.debug(str(self.target.qsize()) + " items in queue a")
            except: # send info to other threads that error occur here, and thread is stopped.
                logging.error("thread dead!")
                self.sigkill.put(self.name)
                return
        return
