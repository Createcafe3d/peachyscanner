import threading
import cv2
import numpy as np

import logging

logger = logging.getLogger('peachy')


class VideoProcessor(threading.Thread):
    def __init__(self, camera, encoder, roi, laser_detector):
        threading.Thread.__init__(self)
        self.camera = camera
        self.running = False
        self.handlers = []
        self.encoder = encoder
        self.roi = roi
        self.laser_detector = laser_detector
        self.image = {'frame': np.ones((10, 10, 3), dtype='uint8') * 255, 'laser_detection': np.zeros((10, 10, 3), dtype='uint8')}

    def run(self):
        logger.info("Starting video capture")
        self.running = True
        while (self.running):
            frame = self.camera.read()
            detected = self.laser_detector.detect(frame)
            should_capture, section = self.encoder.should_capture_frame_for_section(frame)
            if should_capture:
                for handler, callback in self.handlers:
                    roi = self.roi.get_left_of_center(frame)
                    roi_center_y = (frame.shape[0] // 2) - (self.roi.y_rel * frame.shape[0])
                    roi_detected = self.roi.get_left_of_center(detected)
                    result = handler.handle(
                        frame=roi,
                        section=section,
                        roi_center_y=roi_center_y,
                        partial_laser_detection=roi_detected,
                        laser_detection=detected,
                        roi=self.roi
                        )
                    callback(handler)
                    if not result:
                        self.unsubscribe((handler, callback))
            self.image = {'frame': frame, 'laser_detection': detected}
        logger.info("Shutting down")

    def _get_new_size(self, dest_x, dest_y, source_x, source_y):
        source_ratio = source_x / float(source_y)
        dest_ratio = dest_x / float(dest_y)
        if dest_ratio > source_ratio:
            return (int(source_x * dest_y / source_y), int(dest_y))
        else:
            return (int(dest_x), int(source_y * dest_x / source_x))

    def get_bounded_image(self, requested_x, requested_y):
        image = self.image['frame']
        detected = self.image['laser_detection']
        ratio = self._get_new_size(requested_x, requested_y, image.shape[1], image.shape[0])
        if ratio == (0, 0):
            ratio = (1, 1)

        scaled_image = cv2.resize(image, ratio)
        scaled_detected = cv2.resize(detected, ratio)
        roi_frame = self.roi.overlay(scaled_image)
        encoder_overlay = self.encoder.overlay_encoder(scaled_image)
        encoder_history = self.encoder.overlay_history(scaled_image)
        rotation = ((self.encoder.position % self.encoder.sections) / float(self.encoder.sections)) * 360.0
        return {
            'frame': scaled_image,
            'laser_detection': scaled_detected,
            'encoder': encoder_overlay,
            'history': encoder_history,
            'roi_frame': roi_frame,
            'rotation': rotation
        }

    def stop(self):
        self.running = False
        retry_count = 0
        while self.is_alive() and retry_count < 5:
            retry_count += 1
            logger.info("Joining main thread")
            self.join(1)

    def subscribe(self, handler, callback=lambda x: x):
        self.handlers.append((handler, callback))

    def unsubscribe(self, handler):
        self.handlers.remove(handler)
