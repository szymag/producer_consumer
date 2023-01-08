import threading
import logging
import cv2


class ConsumerThread(threading.Thread):
    def __init__(
        self,
        target=None,
        name=None,
        resize_ratio=2,
        kernel=5,
        frame_count=100,
        sigkill=None,
    ):
        super(ConsumerThread, self).__init__()
        self.target, self.target_B = target
        self.name = name
        self.resize_ratio = resize_ratio
        self.kernel = kernel
        self.frame_count = frame_count
        self.sigkill = sigkill
        return

    def run(self):
        idx = 0
        while True:
            if not self.target.empty():
                try:
                    item = self.target.get()
                    self.target_B.put(item)
                    logging.debug(str(self.target.qsize()) + " items in queue a")
                    logging.debug(str(self.target_B.qsize()) + " items in queue b")
                    idx += 1
                except:
                    logging.error("thread dead!")
                    self.sigkill.put(self.name)
                    break
            elif not self.sigkill.empty():
                return
            if idx == self.frame_count:
                break
        return

    def apply_filter(self, picture):
        pass

    def reduce_size(self, picture):
        pass
