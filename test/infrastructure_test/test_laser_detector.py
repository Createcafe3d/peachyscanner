import unittest
import sys
import os
import numpy as np
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.laser_detector import LaserDetector


class LaserDetectorTest(unittest.TestCase):

    def test_raises_exception_if_inverted_values(self):
            with self.assertRaises(Exception):
                LaserDetector((130, 128, 128), (129, 129, 129))
            with self.assertRaises(Exception):
                LaserDetector((128, 130, 128), (129, 129, 129))
            with self.assertRaises(Exception):
                LaserDetector((128, 128, 130), (129, 129, 129))
            with self.assertRaises(Exception):
                LaserDetector((127, 127, 127), (126, 128, 128), )
            with self.assertRaises(Exception):
                LaserDetector((127, 127, 127), (128, 126, 128), )
            with self.assertRaises(Exception):
                LaserDetector((127, 127, 127), (128, 128, 126), )

    def test_from_rgb_float_works_with_expected_range(self):
        low = (0.0, 0.25, 0.5)
        high = (0.5, 0.75, 1.0)
        expected_low = (127, 63, 0)
        expected_high = (255, 191, 127)

        laser_detector = LaserDetector.from_rgb_float(low, high)

        self.assertEquals(laser_detector.low_bgr, expected_low)
        self.assertEquals(laser_detector.high_bgr, expected_high)

    def test_detect_returns_an_empty_matrix_with_nothing_in_range(self):
        test = np.ones((100, 100, 3), dtype='uint8') * 255
        expected = np.zeros((100, 100, 1), dtype='uint8')

        laser_detector = LaserDetector((128, 128, 128), (129, 129, 129))
        result = laser_detector.detect(test)

        self.assertTrue((expected == result).all())

    def test_detect_returns_matrix_of_matched_points_if_in_range(self):
        test = np.ones((10, 10, 3), dtype='uint8') * 129
        expected = np.ones((10, 10, 1), dtype='uint8') * 255

        laser_detector = LaserDetector((128, 128, 128), (130, 130, 130))
        result = laser_detector.detect(test)

        self.assertTrue((expected == result).all(), "{} != {}".format(expected, result) )



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()