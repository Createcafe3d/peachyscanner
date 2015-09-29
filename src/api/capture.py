import numpy as np
import cv2
import cv
import threading
import logging

from camera_control import CameraControl

logger = logging.getLogger('peachy')


class Capture(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        logger.info("Creating Window")
        self.is_running = True
        self.show = 'r'
        self.canny_low = 50
        self.canny_high = 100
        cv.NamedWindow('frame', flags=cv.CV_WINDOW_NORMAL)
        cv2.resizeWindow('frame', 960, 540)
        cv2.setMouseCallback('frame', self.clicky)
        self.mouse_pos = [0, 0]
        self.centre = [0, 0]

        self.show_crosshair = False
        self.display_range = False

        self.cap = cv2.VideoCapture(0)
        self.cap.read()
        self.cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 1080.0)
        self.cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 1920.0)
        self.camera = CameraControl()

        self.lower_range = np.array([50, 50, 180])
        self.upper_range = np.array([255, 255, 255])

        self._left_click_call_backs = []
        self._centre_callback = None

    def clicky(self, event, x, y, flags, param):
        self.mouse_pos = [x, y]
        if event == cv2.EVENT_LBUTTONDOWN:
            while len(self._left_click_call_backs) > 0:
                self._left_click_call_backs.pop()(x, y)

        if event == cv2.EVENT_RBUTTONDOWN:
            pass

    def show_range(self, low_RGB, high_RGB):
        self.display_range = True
        self.lower_range = np.array([min(low_RGB[2], high_RGB[2]) * 255, min(low_RGB[1], high_RGB[1]) * 255, min(low_RGB[0], high_RGB[0]) * 255])
        self.upper_range = np.array([max(low_RGB[2], high_RGB[2]) * 255, max(low_RGB[1], high_RGB[1]) * 255, max(low_RGB[0], high_RGB[0]) * 255])

        logger.info("Upper Range: {}".format(self.upper_range))
        logger.info("Lower Range: {}".format(self.lower_range))

    def hide_range(self):
        self.display_range = False

    def get_centre(self, call_back):
        self.show_crosshair = True
        self._centre_callback = call_back
        self._left_click_call_backs.append(self._set_centre)

    def _set_centre(self, x, y):
        logger.info("Center set to {}, {}".format(x, y))
        self.show_crosshair = False
        self.centre = [x, y]
        if self._centre_callback:
            self._centre_callback([x, y])
            self._centre_callback = None

    def show_data(self):
        for (key, value) in self.video_properties.items():
            logger.info("{} = {}".format(key, self.cap.get(value)))

    def shutdown(self):
        self.is_running = False

    def draw_cross_hair(self, frame):
        cv2.line(frame, (0, self.mouse_pos[1]), (frame.shape[1], self.mouse_pos[1]), (0, 255, 0), 2)
        cv2.line(frame, (self.mouse_pos[0], 0), (self.mouse_pos[0], frame.shape[0]), (0, 255, 0), 2)

    def run(self):
        while(self.is_running):
            ret, frame = self.cap.read()

            if self.display_range:
                mask = cv2.inRange(frame, self.lower_range, self.upper_range)
                b, g, r = cv2.split(frame)
                b = cv2.subtract(b, mask)
                g = cv2.add(g, mask)
                r = cv2.subtract(r, mask)
                frame = cv2.merge((b, g, r))

            if self.show_crosshair:
                self.draw_cross_hair(frame)
            self.frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
            cv2.imshow('frame', self.frame)
            # self.show_data()
            key = chr(cv2.waitKey(1) & 0xFF)
            if key == 'q':
                break
        self.cap.release()
        cv2.destroyAllWindows()