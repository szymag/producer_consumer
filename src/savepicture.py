import threading
import logging
import time
import queue
import cv2
import os
import numpy as np


class SavePictureThread(threading.Thread):
    def __init__(
        self,
        target: queue,
        sigkill: queue,
        name: str = "SavePicture",
        path: str = "./processed/",
        frame_count: int = 100,
    ):
        """Thread responsible for saving data in png format.
        It recieve data from Consumer.
        This thread will overwrite files. 

        Args:
            target (queue): queue B share data between threads.
            sigkill (queue):  queue that is shared between all the threads.
            It keeps track whether any of them is interrupted.
            In such case, the rest should be stopped.
            name (str, optional):  Name of the thread. Defaults to "SavePicture".
            path (str, optional): Place, where files are saved.
            Defaults to "./processed/".
            frame_count (int, optional): How many times data are taken from Source.
            Defaults to 100.
        """
        super(SavePictureThread, self).__init__()
        self.target_B = target
        assert isinstance(self.target_B, queue.Queue)
        self.sigkill = sigkill
        assert isinstance(self.sigkill, queue.Queue)
        self.name = name
        self.path = path
        self.frame_count = frame_count
        assert (isinstance(self.frame_count, int) and self.frame_count > 0
        ), "Number of data must be natural number bigger than 0"
        try:
            os.mkdir(self.path) # make a directory for files
        except:
            logging.warning("Use existing directory. Files can be overwritten.")
            pass # if directory already exist, move on
        return

    def run(self):
        idx = 0
        while True:
            if not self.target_B.empty():
                try:
                    item = self.target_B.get()
                    self.save_png(item, idx)
                    logging.debug(str(self.target_B.qsize()) + " items in queue b")
                    idx += 1
                except: # send info to other threads that error occur here, and thread is stopped.
                    logging.error("thread dead!")
                    self.sigkill.put(self.name)
                    break
            elif not self.sigkill.empty(): # stop thread if error occur in other threads
                break
            if idx == self.frame_count: # stop thread when all data are processed
                break
        return

    def save_png(self, arr, idx):
        """Save picture to png file. 

        Args:
            arr (np.ndarray): Picture.
            idx (int): Index of picture. 
        """
        logging.debug(f"{self.path}{idx}.png saved")
        cv2.imwrite(f"{self.path}{idx}.png", arr)
