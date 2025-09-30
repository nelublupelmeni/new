import cv2
import numpy as np
import os

def add_sepia(image, strength=0.8):
    """
    Накладывает эффект сепии.
    """
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia_img = cv2.transform(image, sepia_filter)
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    output = cv2.addWeighted(image, 1 - strength, sepia_img, strength, 0)
    return output
