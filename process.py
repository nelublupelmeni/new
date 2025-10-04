import cv2
import numpy as np
import os
from PIL import Image
from effects.noise import add_noise
from effects.scratchers import add_scratches
from effects.sepia import add_sepia

def process_image(file, params, preview_size=None):
    """основная функция обработки изображения - применяет все эффекты старения"""
    try:
        # читаем изображение из загруженного файла
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # проверяем что изображение загрузилось корректно
        if image is None:
            return None
        
        # если нужно превью - уменьшаем размер для скорости обработки
        if preview_size:
            height, width = image.shape[:2]
            if width > preview_size:
                scale = preview_size / width
                new_width = preview_size
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # создаем копию изображения для применения эффектов
        result = image.copy()
        
        # применяем эффект сепии если сила эффекта больше нуля
        sepia_strength = float(params.get('sepia_strength', 0))
        if sepia_strength > 0:
            result = add_sepia(result, sepia_strength)
        
        # добавляем шум если интенсивность больше нуля
        noise_intensity = float(params.get('noise_intensity', 0))
        if noise_intensity > 0:
            result = add_noise(result, intensity=noise_intensity)
        
        # добавляем царапины если пользователь включил эту опцию
        if params.get('add_scratches') == 'true':
            scratches_folder = "scratches"
            # проверяем что папка с царапинами существует
            if os.path.exists(scratches_folder):
                result = add_scratches(
                    result,
                    scratches_folder,
                    alpha=float(params.get('scratches_alpha', 0.5)),
                    density=int(params.get('scratches_density', 5)),
                    size_range=(
                        float(params.get('scratches_min_size', 0.1)),
                        float(params.get('scratches_max_size', 0.3))
                    ),
                    rotation_range=(-180, 180)
                )
        
        # конвертируем обратно в PIL Image для удобного сохранения
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(result_rgb)
        
        return pil_image
        
    except Exception as e:
        # пробрасываем исключение дальше для обработки в вызывающем коде
        raise e

def create_preview(file, params):
    """создает уменьшенное превью для быстрого предпросмотра в реальном времени"""
    # сбрасываем позицию файла на случай повторного использования
    file.seek(0)
    # обрабатываем изображение с уменьшенным размером для скорости
    return process_image(file, params, preview_size=600)