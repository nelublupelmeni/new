import cv2
import numpy as np
import os
import random

def add_noise(image, intensity=25, seed=None):
    """
    Добавляет гауссов шум к изображению.
    intensity: стандартное отклонение шума
    seed: фиксированное зерно для генератора (чтобы шум не менялся случайно)
    """
    noisy = image.astype(np.float32)
    rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()
    noise = rng.normal(0, intensity, image.shape).astype(np.float32)
    noisy += noise
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

