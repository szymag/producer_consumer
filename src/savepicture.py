import threading
import logging
import time
import cv2
import os


class SavePictureThread(threading.Thread):
    def __init__(
        self, target=None, name=None, path=None, frame_count=100, sigkill=None
    ):
        super(SavePictureThread, self).__init__()
        self.target_B = target
        self.name = name
        self.path = path
        self.frame_count = frame_count
        self.sigkill = sigkill
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
                logging.info(str(self.target_B.qsize()) + " items in queue b")
                idx += 1
            elif not self.sigkill.empty():
                break
            if idx == self.frame_count:
                break
        return

    def save_png(self, arr, idx):
        # print(f"{self.path}/{idx}.png")
        cv2.imwrite(f"{self.path}{idx}.png", arr)
