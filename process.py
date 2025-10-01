import cv2
import numpy as np
import os
from PIL import Image
from effects.noise import add_noise
from effects.scratchers import add_scratches
from effects.sepia import add_sepia

def process_image(file, params, preview_size=None):
    """Основная функция обработки изображения"""
    try:
        # Чтение изображения
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return None
        
        # Если нужно превью - уменьшаем размер для скорости
        if preview_size:
            height, width = image.shape[:2]
            if width > preview_size:
                scale = preview_size / width
                new_width = preview_size
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        result = image.copy()
        
        # Применение сепии
        sepia_strength = float(params.get('sepia_strength', 0))
        if sepia_strength > 0:
            result = add_sepia(result, sepia_strength)
        
        # Добавление шума
        noise_intensity = float(params.get('noise_intensity', 0))
        if noise_intensity > 0:
            result = add_noise(result, intensity=noise_intensity)
        
        # Добавление царапин (если запрошено)
        if params.get('add_scratches') == 'true':
            scratches_folder = "scratches"
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
        
        # Конвертация обратно в PIL Image для сохранения
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(result_rgb)
        
        return pil_image
        
    except Exception as e:
        raise e

def create_preview(file, params):
    """Создает превью для реального времени"""
    # Сбрасываем позицию файла на случай повторного использования
    file.seek(0)
    return process_image(file, params, preview_size=600)

def get_file_extension(format_name):
    """Возвращает расширение файла для формата"""
    extensions = {
        'JPEG': '.jpg',
        'PNG': '.png',
        'WEBP': '.webp',
        'BMP': '.bmp'
    }
    return extensions.get(format_name.upper(), '.jpg')

def save_image(pil_image, filepath, format_name, quality=85):
    """Сохраняет изображение в указанном формате с настройками качества"""
    format_name = format_name.upper()
    
    save_params = {}
    
    if format_name in ['JPEG', 'WEBP']:
        save_params['quality'] = quality
        if format_name == 'JPEG':
            # Для JPEG конвертируем в RGB если нужно
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
        elif format_name == 'WEBP':
            save_params['quality'] = quality
    
    elif format_name == 'PNG':
        save_params['optimize'] = True
    
    pil_image.save(filepath, format=format_name, **save_params)
    return filepath