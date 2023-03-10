import threading
import queue
import logging
import numpy as np
import cv2


class ConsumerThread(threading.Thread):
    def __init__(
        self,
        target: (queue, queue),
        sigkill: queue,
        name: str = "Consumer",
        resize_ratio: float = 2,
        kernel: int = 5,
        frame_count: int = 100,
    ):
        """Thread that recieve data from Producer via queue A, process and the send to queue B.
        Median filter and reduction of size is applied on the data.

        Args:
            target (queue, queue): queue share data between threads.
            Here, two queue are provided because data are moved from Producer to SavePicture.
            sigkill (queue, optional): queue that is shared between all the threads.
            It keeps track whether any of them is interrupted.
            In such case, the rest should be stopped.
            name (str, optional): Name of the thread. Defaults to Consumer.
            resize_ratio (float, optional): Determine how many times picture should be resized. Defaults to 2.
            kernel (int, optional): Define kernel of median filter. Defaults to 5.
            frame_count (int, optional): How many times data are taken from Source. Defaults to 100.
        """
        super(ConsumerThread, self).__init__()
        self.target, self.target_B = target
        assert isinstance(self.target, queue.Queue)
        assert isinstance(self.target_B, queue.Queue)
        self.sigkill = sigkill
        assert isinstance(self.sigkill, queue.Queue)
        self.name = name
        self.resize_ratio = resize_ratio
        self.kernel = kernel
        self.frame_count = frame_count
        assert (isinstance(self.frame_count, int) and self.frame_count > 0
        ), "Number of data must be natural number bigger than 0"
        
        return

    def run(self):
        idx = 0
        while True:
            if not self.target.empty():
                try:
                    item = self.target.get()
                    item = self.reduce_size(item)
                    item = self.apply_filter(item)
                    self.target_B.put(item)
                    logging.debug(str(self.target.qsize()) + " items in queue a")
                    logging.debug(str(self.target_B.qsize()) + " items in queue b")
                    idx += 1
                except: # send info to other threads that error occur here, and thread is stopped.
                    logging.error("thread dead!")
                    self.sigkill.put(self.name)
                    break
            elif not self.sigkill.empty(): # stop thread if error occur in other threads
                return
            if idx == self.frame_count: # stop thread when all data are processed
                break
        return

    def apply_filter(self, picture):
        """Apply median filter on picture. It uses opencv implementation.
        Kernel size is defined in constructor of the class, defaults to 5.

        Args:
            picture (np.ndarray): Picture.

        Returns:
            np.ndarray: Picture.
        """
        return cv2.medianBlur(picture, ksize=self.kernel)

    def reduce_size(self, picture):
        """Reduce size of picture. It uses default nearest-neighbor
        interpolation. Dimensions are changed accordingly to resize_ratio
        set in class constructor. It preserves aspect ratio.

        Args:
            picture (np.ndarray): _description_

        Returns:
            np.ndarray: Resized picture.
        """
        width = int(picture.shape[1] / self.resize_ratio)
        height = int(picture.shape[0] / self.resize_ratio)
        new_dim = (width, height)
        return cv2.resize(picture, new_dim)
