import unittest
import queue
import shutil
import os
import cv2
import numpy as np
from src.source import Source
from src.producer import ProducerThread
from src.consumer import ConsumerThread
from src.savepicture import SavePictureThread


class TestProducerThread(unittest.TestCase):
    def setUp(self):
        self.q_a = queue.Queue()
        self.queue_errors = queue.Queue()

    def test_production_1(self):
        producer = ProducerThread(
            target=self.q_a, frame_count=10, sigkill=self.queue_errors
        )
        producer.start()
        producer.join()

        self.assertEqual(self.q_a.qsize(), producer.frame_count)
        for i in range(producer.frame_count):
            el = self.q_a.get()
            self.assertEqual(el.shape, (*producer.picture_shape, 3))

    def test_production_2(self):
        producer = ProducerThread(
            target=self.q_a,
            picture_shape=(100, 50),
            sigkill=self.queue_errors,
        )
        producer.start()
        producer.join()

        self.assertEqual(self.q_a.qsize(), producer.frame_count)
        for i in range(producer.frame_count):
            el = self.q_a.get()
            self.assertEqual(el.shape, (100, 50, 3))

    def test_production_3(self):
        with self.assertRaises(AssertionError):
            ProducerThread(
                target=self.q_a,
                name="Producer",
                frame_count=15,
                picture_shape=(0, 50),
                sigkill=self.queue_errors,
            )
        with self.assertRaises(AssertionError):
            ProducerThread(
                target=self.q_a,
                name="Producer",
                frame_count=15,
                picture_shape=(40, 45.4),
                sigkill=self.queue_errors,
            )


class TestConsumerThread(unittest.TestCase):
    def setUp(self):
        self.q_a = queue.Queue()
        self.q_b = queue.Queue()
        self.queue_errors = queue.Queue()

    def test_consumption_1(self):
        producer = ProducerThread(
            target=self.q_a,
            sigkill=self.queue_errors,
        )
        producer.start()

        consumer = ConsumerThread(
            target=(self.q_a, self.q_b),
            sigkill=self.queue_errors,
        )
        consumer.start()
        producer.join()
        consumer.join()

        self.assertEqual(self.q_b.qsize(), producer.frame_count)
        self.assertEqual(self.q_a.qsize(), 0)
        for i in range(consumer.frame_count):
            self.assertEqual(self.q_b.get().shape, (384, 512, 3))

    def test_consumption_2(self):
        producer = ProducerThread(
            target=self.q_a,
            frame_count=15,
            picture_shape=(100, 50),
            sigkill=self.queue_errors,
        )
        producer.start()

        consumer = ConsumerThread(
            target=(self.q_a, self.q_b),
            frame_count=15,
            sigkill=self.queue_errors,
        )
        consumer.start()
        producer.join()
        consumer.join()

        self.assertEqual(self.q_b.qsize(), producer.frame_count)
        self.assertEqual(self.q_a.qsize(), 0)
        for i in range(15):
            self.assertEqual(self.q_b.get().shape, (50, 25, 3))


    def test_consumption_2(self):
        producer = ProducerThread(
            target=self.q_a,
            frame_count=5,
            sigkill=self.queue_errors,
        )
        producer.start()

        consumer = ConsumerThread(
            target=(self.q_a, self.q_b),
            frame_count=5,
            sigkill=self.queue_errors,
            resize_ratio=1.5
        )
        consumer.start()
        producer.join()
        consumer.join()

        self.assertEqual(self.q_b.qsize(), producer.frame_count)
        self.assertEqual(self.q_a.qsize(), 0)
        for i in range(5):
            self.assertEqual(self.q_b.get().shape, (int(768/1.5), int(1024/1.5), 3))

    def test_apply_filter(self):
        """ Test if filter method return picture with correct dimensions.
        """
        consumer = ConsumerThread(
            target=(self.q_a, self.q_b),
            sigkill=self.queue_errors,
        )
        picture_1 = cv2.imread('./test_pictures/test_0.png')
        picture_2 = consumer.apply_filter(picture_1)
        self.assertEqual(picture_1.shape, picture_2.shape)

class TestResize(unittest.TestCase):
    """Test resize. Resize shouldn't affect the picture, so here 
    are compared histogram of orginal and modified pictures to dermine if 
    function correclty resize. 
    This method will not work with white noise data, because in resize 
    interpolation is used, so uniform distribution will be affected.
    """
    def setUp(self):
        self.q_a = queue.Queue()
        self.q_b = queue.Queue()
        self.queue_errors = queue.Queue()
        self.consumer = ConsumerThread(target=(self.q_a, self.q_b),
        sigkill=self.queue_errors, resize_ratio=2)
    
    def test_resize_1(self):
        picture_1 = cv2.imread('./test_pictures/test_0.png')
        picture_2 = self.consumer.reduce_size(picture_1)
        for channel in range(3):
            hist1 = cv2.calcHist([picture_1], [channel], None, [256], [0, 256]).T
            hist2 = cv2.calcHist([picture_2], [channel], None, [256], [0, 256]).T
            hist_area1 = np.trapz(hist1/np.max(hist1))
            hist_area2 = np.trapz(hist2/np.max(hist2))
            # check if all channel are not modified by more than 10%
            self.assertTrue(abs(hist_area1-hist_area2)/hist_area1 < 0.1)

    def test_resize_2(self):
        picture_1 = cv2.imread('./test_pictures/test_1.png')
        picture_2 = self.consumer.reduce_size(picture_1)
        for channel in range(3):
            hist1 = cv2.calcHist([picture_1], [channel], None, [256], [0, 256]).T
            hist2 = cv2.calcHist([picture_2], [channel], None, [256], [0, 256]).T
            hist_area1 = np.trapz(hist1/np.max(hist1))
            hist_area2 = np.trapz(hist2/np.max(hist2))
            # check if all channel are not modified by more than 10%
            self.assertTrue(abs(hist_area1-hist_area2)/hist_area1 < 0.1)

    def test_resize_3(self):
        picture_1 = cv2.imread('./test_pictures/test_2.png')
        picture_2 = self.consumer.reduce_size(picture_1)
        for channel in range(3):
            hist1 = cv2.calcHist([picture_1], [channel], None, [256], [0, 256]).T
            hist2 = cv2.calcHist([picture_2], [channel], None, [256], [0, 256]).T
            hist_area1 = np.trapz(hist1/np.max(hist1))
            hist_area2 = np.trapz(hist2/np.max(hist2))
            # check if all channel are not modified by more than 10%
            self.assertTrue(abs(hist_area1-hist_area2)/hist_area1 < 0.1)


class TestSavePictureThread(unittest.TestCase):
    def setUp(self):
        self.q_a = queue.Queue()
        self.q_b = queue.Queue()
        self.queue_errors = queue.Queue()
        self.fr_count = 55

    def tearDown(self):
        shutil.rmtree("./test_processed")

    def test_seve_picture_1(self):
        producer = ProducerThread(
            target=self.q_a,
            name="Producer",
            frame_count=self.fr_count,
            picture_shape=(100, 50),
            sigkill=self.queue_errors,
        )
        producer.start()
        consumer = ConsumerThread(
            target=(self.q_a, self.q_b),
            name="Consumer",
            frame_count=self.fr_count,
            sigkill=self.queue_errors,
        )
        consumer.start()

        save_pic = SavePictureThread(
            target=self.q_b,
            name="Save picture",
            path="./test_processed/",
            frame_count=self.fr_count,
            sigkill=self.queue_errors,
        )
        save_pic.start()

        producer.join()
        consumer.join()
        save_pic.join()

        self.assertEqual(len(os.listdir("./test_processed/")), 55)


if __name__ == "__main__":
    unittest.main()
