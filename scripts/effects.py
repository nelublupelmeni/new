import cv2
import numpy as np
import os

def add_noise(image, intensity=25):
    """
    Добавляет гауссов шум к изображению.
    intensity: стандартное отклонение шума (чем больше, тем сильнее зернистость).
    """
    noisy = image.astype(np.float32)
    noise = np.random.normal(0, intensity, image.shape).astype(np.float32)
    noisy += noise
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

def add_sepia(image, strength=0.8):
    """
    Накладывает эффект сепии.
    strength: от 0 (нет эффекта) до 1 (максимальная сепия).
    """
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])#стандартная цветовая трансформационная матрица для эффекта сепии
    
    sepia_img = cv2.transform(image, sepia_filter)
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    output = cv2.addWeighted(image, 1 - strength, sepia_img, strength, 0)
    return output

def add_scratches(image, scratch_path, alpha):
    """
    Накладывает царапины поверх изображения.
    scratch_path: путь к PNG-файлу с царапинами 
    alpha: прозрачность наложения (0-1)
    """
    scratches = cv2.imread(scratch_path, cv2.IMREAD_UNCHANGED)
    if scratches is None:
        print(f"Не удалось загрузить файл царапин: {scratch_path}")
        return image
     # Масштабируем под размер фото
    scratches = cv2.resize(scratches, (image.shape[1], image.shape[0]))
    # Разделяем каналы
    scratch_rgb = scratches[:, :, :3]
    scratch_alpha = scratches[:, :, 3] / 255.0  # диапазон от 0 до 1
    
    # Дополнительно уменьшаем/усиливаем прозрачность по параметру alpha
    scratch_alpha = np.clip(scratch_alpha * alpha, 0, 1)
    
    # Преобразуем к 3 каналам, чтобы умножать на RGB
    scratch_alpha_3c = cv2.merge([scratch_alpha, scratch_alpha, scratch_alpha])
    
    # Смешиваем изображения (альфа-смешивание)
    overlay = (scratch_rgb * scratch_alpha_3c + image * (1 - scratch_alpha_3c)).astype(np.uint8)
    
    return overlay

def process_image_dynamic(input_path, output_folder="output", scratch_path=None,
                          sepia=0.8, noise=30, scratch_alpha=0.6):
    """
    Обрабатывает изображение: шум -> сепия -> царапины.
    """
    # Загружаем изображение
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Изображение не найдено: {input_path}")

    # Применяем эффекты по параметрам
    if noise > 0:
        img = add_noise(img, intensity=noise)
    if sepia > 0:
        img = add_sepia(img, strength=sepia)
    if scratch_path and scratch_alpha > 0:
        img = add_scratches(img, scratch_path, alpha=scratch_alpha)

    # Если указан output_folder, сохраняем
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_folder, f"final_{filename}")
        cv2.imwrite(output_path, img)

    return img
