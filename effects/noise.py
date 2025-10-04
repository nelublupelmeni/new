import cv2
import numpy as np
import os
import random

def add_noise(image, intensity=25, seed=None):
    """
    Добавляет гауссов шум к изображению

    Аргументы:
    image: исходное изображение
    intensity: стандартное отклонение шума или сила эффекта
    seed: фиксированное значение для воспроизводимости результата
    """
    # Конвертируем изображение в float32 для математических операций
    noisy = image.astype(np.float32)
    # Создаем генератор случайных чисел с фиксированным seed или случайным
    rng = np.random.default_rng(seed) if seed is not None else np.random.default_rng()
    # Генерируем гауссов шум с нулевым средним и заданной интенсивностью
    noise = rng.normal(0, intensity, image.shape).astype(np.float32)
    # Добавляем шум к исходному изображению
    noisy += noise
    # Обрезаем значения пикселей до допустимого диапазона 0-255
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    
    return noisy