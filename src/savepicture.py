import threading
import logging
import time
import queue
import cv2
import os


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
        self.sigkill = sigkill
        self.name = name
        self.path = path
        self.frame_count = frame_count

        try:
            os.mkdir(self.path)
        except:
            pass
        return

    def run(self):
        idx = 0
        while True:
            if not self.target_B.empty():
                item = self.target_B.get()
                self.save_png(item, idx)
                logging.debug(str(self.target_B.qsize()) + " items in queue b")
                idx += 1
            elif not self.sigkill.empty():
                break
            if idx == self.frame_count:
                break
        return

    def save_png(self, arr, idx):
        # print(f"{self.path}/{idx}.png")
        cv2.imwrite(f"{self.path}{idx}.png", arr)
