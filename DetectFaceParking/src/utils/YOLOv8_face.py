from collections.abc import Iterable

import cv2
import numpy as np


class YoloMask():
    def __init__(self):
        self.expand = 1.0
        # self.expand=1.2
        self.min_face_size = 0
        self.conf_thres = 0.3

    def able_to_align(self):
        return True

    def detect(self, srcimg, results=None):
        results = results[0].cpu().numpy()
        iheight, iwidth, _ = srcimg.shape

        bounding_boxes, conf, faces = [], [], []

        for bbox, lmks in zip(results.boxes, results.keypoints.xy):
            x, y, w, h = bbox.xywh[0]
            x, y, w, h = int(x - w / 2), int(y - h / 2), int(w), int(h)

            if w != h:
                if w > h:
                    y = y - (w - h) // 2
                    h = w
                else:
                    x = x - (h - w) // 2
                    w = h

            x = x - (w * self.expand - w) // 2
            y = y - (h * self.expand - h) // 2
            h *= self.expand
            w *= self.expand
            if x < 0:
                x = 0
            if x + w >= iwidth:
                x = iwidth - w - 1
            if y < 0:
                y = 0
            if y + h >= iheight:
                y = iheight - h - 1

            if self.min_face_size is not None:
                if isinstance(self.min_face_size, Iterable) and len(self.min_face_size) == 2:
                    e_w, e_h = self.min_face_size
                else:
                    e_w = e_h = self.min_face_size
                if w < e_w or h < e_h:
                    continue

            if bbox.conf[0] < self.conf_thres:
                continue
            bounding_boxes.append([x, y, w, h])
            conf.append(bbox.conf[0])
            faces.append({
                'left_eye': lmks[0].astype(np.int16),
                'right_eye': lmks[1].astype(np.int16),
                'nose': lmks[2].astype(np.int16),
                'mouth_left': lmks[3].astype(np.int16),
                'mouth_right': lmks[4].astype(np.int16),
            })

        return np.array(bounding_boxes), np.array(conf), faces
