import cv2
import numpy as np
import os
import random

def add_noise(image, intensity):
    """
    Добавляет гауссов шум к изображению.
    intensity: стандартное отклонение шума (сила эффекта).
    """
    # Конвертируем изображение в вещественные числа для расчетов
    noisy = image.astype(np.float32)
    # Генерируем случайный шум с нормальным распределением
    noise = np.random.normal(0, intensity, image.shape).astype(np.float32)
    # Добавляем шум к исходному изображению
    noisy += noise
    # Обрезаем значения чтобы они остались в диапазоне 0-255
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    
    return noisy