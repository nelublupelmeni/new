import cv2
import numpy as np
import os

def apply_noise(image, intensity=25):
    """
    Добавляет гауссов шум к изображению.
    intensity: стандартное отклонение шума (чем больше, тем сильнее зернистость).
    """
    noisy = image.astype(np.float32)
    noise = np.random.normal(0, intensity, image.shape).astype(np.float32)
    noisy += noise
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

def apply_sepia(image, strength=0.8):
    """
    Накладывает эффект сепии.
    strength: от 0 (нет эффекта) до 1 (максимальная сепия).
    """
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    
    sepia_img = cv2.transform(image, sepia_filter)
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    output = cv2.addWeighted(image, 1 - strength, sepia_img, strength, 0)
    return output

def process_image(input_path, output_folder="output"):
    # Загружаем изображение
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Изображение не найдено: {input_path}")
    
    # Последовательное применение эффектов: шум -> сепия
    noisy_img = apply_noise(img, intensity=30)
    noisy_sepia_img = apply_sepia(noisy_img, strength=0.8)
    
    # Создаём папку output, если её нет
    os.makedirs(output_folder, exist_ok=True)
    
    # Генерируем имя выходного файла
    filename = os.path.basename(input_path)
    output_path = os.path.join(output_folder, f"noisy_sepia_{filename}")
    
    # Сохраняем результат
    cv2.imwrite(output_path, noisy_sepia_img)
    print(f"Обработанное изображение сохранено в: {output_path}")

if __name__ == "__main__":
    # Пример запуска
    test_image = "c:/smdvorkina/test_photos/istockphoto-949483148-1024x1024.jpg"  # укажи свой путь
    process_image(test_image)
