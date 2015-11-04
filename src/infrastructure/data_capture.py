import numpy as np
import logging

logger = logging.getLogger('peachy')


class ImageCapture(object):

    def __init__(self, sections):
        self.sections = sections
        self._section_count = 0
        self.image = None

    @property
    def complete(self):
        return self._section_count >= self.sections

    def handle(self, frame=None, section=0, **kwargs):
        self._section_count += 1
        self._image(frame.shape[0])[:, section] = frame[:, -1]
        return self._section_count < self.sections

    def _image(self, y_axis_dimension):
        if self.image is None:
            self.image = np.zeros((y_axis_dimension, self.sections, 3), dtype='uint8')
        return self.image


class PointCapture(object):

    def __init__(self, sections):
        self.sections = sections
        self._section_count = 0
        self.point_converter = PointConverter()
        self.points_tyr = None  #(theta, height, radius)

    @property
    def complete(self):
        return self._section_count >= self.sections

    def handle(self, laser_detection=None, section=0, roi_center_y=0, **kwargs):
        self._section_count += 1
        points = self._points(laser_detection.shape[0])
        points[section] = self.point_converter.get_points(laser_detection, laser_detection.shape[0])
        return self._section_count < self.sections

    def _points(self, height):
        if self.points_tyr is None:
            self.points_tyr = np.zeros((self.sections, height), dtype='int32')
        return self.points_tyr


class PointConverter(object):
    def get_points(self, mask, center_y):
        roi = np.fliplr(mask)
        maxindex = np.argmax(roi, axis=1)
        # maxindex = np.ones(maxindex.shape[0]) * np.linspace(0, 100, maxindex.shape[0])
        return maxindex
