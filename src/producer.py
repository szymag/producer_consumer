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
            target (queue): queue share data are placed.
            sigkill (queue, optional): queue that is shared between all the threads.
            It keeps track wheather any of them is interrupted.
            In such case, the rest should be stopped.
            name (str, optional): Name of the thread. Defaults to Producer.
            frame_count (int, optional): How many times data are taken from Source.
            Defaults to 100.
            picture_shape (tuple, optional): _description_. Defaults to (768, 1024).

        """
        super(ProducerThread, self).__init__()
        self.target = target
        self.name = name
        self.frame_count = frame_count
        self.picture_shape = picture_shape
        assert (
            self.picture_shape[0] > 0
            and self.picture_shape[1] > 0
            and isinstance(self.picture_shape[0], int)
            and isinstance(self.picture_shape[1], int)
        ), "Dimensions of picture must be natural numer bigger that 0"
        self.source = Source((*picture_shape, 3))
        self.delay_frame = 0.05
        self.sigkill = sigkill
        return

    def run(self):
        for i in range(self.frame_count):
            try:
                item = self.source.get_data()
                self.target.put(item)
                time.sleep(self.delay_frame)
                logging.debug(str(self.target.qsize()) + " items in queue a")
            except:
                logging.error("thread dead!")
                self.sigkill.put(self.name)
                return

        return
