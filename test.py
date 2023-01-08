import unittest
import queue
import shutil
import os

# import exception
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
            target=self.q_a,
            name="Producer",
            frame_count=10,
            sigkill=self.queue_errors
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
            name="Producer",
            picture_shape=(100, 50),
            sigkill=self.queue_errors
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
                sigkill=self.queue_errors
            )
        with self.assertRaises(AssertionError):
            ProducerThread(
                target=self.q_a,
                name="Producer",
                frame_count=15,
                picture_shape=(40, 45.4),
                sigkill=self.queue_errors
            )


class TestConsumerThread(unittest.TestCase):
    def setUp(self):
        self.q_a = queue.Queue()
        self.q_b = queue.Queue()
        self.queue_errors = queue.Queue()


    def test_consumption_1(self):
        producer = ProducerThread(
            target=self.q_a,
            name="Producer",
            frame_count=15,
            picture_shape=(100, 50),
            sigkill=self.queue_errors
        )
        producer.start()

        consumer = ConsumerThread(
            target=(self.q_a, self.q_b),
            name="producer",
            frame_count=15,
            sigkill=self.queue_errors
        )
        consumer.start()
        producer.join()
        consumer.join()

        self.assertEqual(self.q_b.qsize(), producer.frame_count)
        self.assertEqual(self.q_a.qsize(), 0)
        for i in range(15):
            self.assertEqual(self.q_b.get().shape, (100, 50, 3))

    def test_consumption_2(self):
        producer = ProducerThread(
            target=self.q_a,
            name="Producer",
            frame_count=15,
            picture_shape=(100, 50),
            sigkill=self.queue_errors
        )
        producer.start()
        consumer = ConsumerThread(
            target=(self.q_a, self.q_b),
            name="Consumer",
            frame_count=15,
            sigkill=self.queue_errors
        )
        consumer.start()
        producer.join()
        consumer.join()

        self.assertEqual(self.q_b.qsize(), producer.frame_count)
        self.assertEqual(self.q_a.qsize(), 0)


class TestSavePictureThread(unittest.TestCase):
    def setUp(self):
        self.q_a = queue.Queue()
        self.q_b = queue.Queue()
        self.queue_errors = queue.Queue()
        self.fr_count = 15

    def tearDown(self):
        shutil.rmtree("./test_processed")

    def test_seve_picture_1(self):
        producer = ProducerThread(
            target=self.q_a,
            name="Producer",
            frame_count=self.fr_count,
            picture_shape=(100, 50),
            sigkill=self.queue_errors
        )
        producer.start()
        consumer = ConsumerThread(
            target=(self.q_a, self.q_b),
            name="Consumer",
            frame_count=self.fr_count,
            sigkill=self.queue_errors
        )
        consumer.start()

        save_pic = SavePictureThread(
            target=self.q_b,
            name="Save picture",
            path="./test_processed/",
            frame_count=self.fr_count,
            sigkill=self.queue_errors
        )
        save_pic.start()

        producer.join()
        consumer.join()
        save_pic.join()

        self.assertEqual(len(os.listdir("./test_processed/")), 15)



if __name__ == "__main__":
    unittest.main()
