import cv2
import os
import random
import numpy as np

def add_scratches(image, scratch_folder, alpha, density, size_range, rotation_range):
    """
    Накладывает случайные царапины поверх изображения.
    Царапины могут свободно пересекать границы зон.
    
    Аргументы:
    image: исходное изображение в формате numpy array
    scratch_folder: путь к папке с PNG-файлами царапин
    alpha: прозрачность наложения (0-1)
    density: количество царапин для наложения
    size_range: диапазон масштабирования царапин (мин, макс)
    rotation_range: диапазон углов поворота в градусах (мин, макс)
    """
    # Загружаем все PNG-файлы из указанной папки
    scratch_files = [os.path.join(scratch_folder, f) for f in os.listdir(scratch_folder) if f.lower().endswith(".png")]
    
    # Проверяем, что в папке есть PNG-файлы
    if not scratch_files:
        print("В папке с царапинами нет PNG-файлов!")
        return image

    # Создаем копию исходного изображения для работы
    overlay = image.copy()
    
    # Получаем размеры исходного изображения
    height, width = image.shape[:2]
    
    # Создаем зоны для базового распределения царапин
    zones = [
        (0, 0, width//2, height//2),           # Верхний левый угол
        (width//2, 0, width, height//2),       # Верхний правый угол
        (0, height//2, width//2, height),      # Нижний левый угол
        (width//2, height//2, width, height)   # Нижний правый угол
    ]
    
    # Распределяем царапины по зонам для стартовых позиций
    # Вычисляем сколько царапин должно быть в каждой зоне
    scratches_per_zone = density // len(zones)  # Базовая часть (поровну на зону)
    extra_scratches = density % len(zones)      # Остаток (лишние царапины)
    
    # Обрабатываем каждую зону
    for zone_idx, zone in enumerate(zones):
        # Извлекаем координаты текущей зоны
        zone_x1, zone_y1, zone_x2, zone_y2 = zone
        
        # Вычисляем сколько царапин будет в этой зоне
        # Первые несколько зон получают по одной дополнительной царапине из остатка
        zone_scratches = scratches_per_zone + (1 if zone_idx < extra_scratches else 0)
        
        # Создаем царапины для текущей зоны
        for _ in range(zone_scratches):
            # Выбираем случайный файл царапины из списка
            scratch_path = random.choice(scratch_files)
            
            # Загружаем изображение царапины с альфа-каналом (прозрачностью)
            scratches = cv2.imread(scratch_path, cv2.IMREAD_UNCHANGED)
            
            # Пропускаем если файл не загрузился
            if scratches is None:
                continue

            # Масштабирование царапины
            # Генерируем случайный коэффициент масштабирования из заданного диапазона
            scale = random.uniform(size_range[0], size_range[1])
            
            # Вычисляем новые размеры царапины после масштабирования
            new_w = int(scratches.shape[1] * scale)
            new_h = int(scratches.shape[0] * scale)
            
            # Изменяем размер царапины с использованием интерполяции AREA (хорошо для уменьшения)
            scratches = cv2.resize(scratches, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # Базовая позиция в зоне, но может выходить за ее пределы
            # Вычисляем центр текущей зоны для базового позиционирования
            zone_center_x = (zone_x1 + zone_x2) // 2
            zone_center_y = (zone_y1 + zone_y2) // 2
            
            # Вычисляем максимальное смещение от центра зоны
            # Ограничиваем смещение чтобы не уходить слишком далеко от изображения
            max_offset_x = min(zone_center_x, width - zone_center_x, new_w * 2)
            max_offset_y = min(zone_center_y, height - zone_center_y, new_h * 2)
            
            # Генерируем случайное смещение от центра зоны (может быть отрицательным)
            offset_x = random.randint(-max_offset_x, max_offset_x)
            offset_y = random.randint(-max_offset_y, max_offset_y)
            
            # Вычисляем конечную позицию царапины
            # Центрируем царапину относительно точки позиционирования + случайное смещение
            x = zone_center_x - new_w // 2 + offset_x
            y = zone_center_y - new_h // 2 + offset_y

            # Поворот царапины
            # Генерируем случайный угол поворота из заданного диапазона
            angle = random.uniform(rotation_range[0], rotation_range[1])
            
            # Вычисляем центр вращения (середина изображения царапины)
            center = (new_w // 2, new_h // 2)
            
            # Создаем матрицу поворота
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Применяем поворот к изображению царапины
            scratches = cv2.warpAffine(
                scratches, 
                rotation_matrix, 
                (new_w, new_h),  # Сохраняем исходные размеры
                flags=cv2.INTER_LINEAR,          # Метод интерполяции
                borderMode=cv2.BORDER_CONSTANT,  # Способ обработки границ
                borderValue=(0, 0, 0, 0)         # Прозрачный фон для RGBA
            )

            # Разделение каналов изображения царапины
            if scratches.shape[2] == 4:  # Если есть альфа-канал (PNG с прозрачностью)
                scratch_rgb = scratches[:, :, :3]      # Берем только цветовые каналы (BGR)
                scratch_alpha = scratches[:, :, 3] / 255.0  # Альфа-канал нормализуем от 0 до 1
            else:  # Если нет альфа-канала
                scratch_rgb = scratches  # Используем все каналы как цветовые
                scratch_alpha = np.ones(scratch_rgb.shape[:2], dtype=np.float32)  # Создаем полностью непрозрачную маску

            # Настройка прозрачности
            # Умножаем исходную прозрачность на параметр alpha и ограничиваем значения от 0 до 1
            scratch_alpha = np.clip(scratch_alpha * alpha, 0, 1)

            # Преобразование маски в 3 канала
            # Создаем 3-канальную маску для смешивания с цветным изображением
            scratch_alpha_3c = cv2.merge([scratch_alpha, scratch_alpha, scratch_alpha])

            # Обрезка только по границам всего изображения
            # Вычисляем реальные координаты с учетом границ всего изображения
            start_x = max(0, x)                    # Начало по X (не меньше 0)
            start_y = max(0, y)                    # Начало по Y (не меньше 0)
            end_x = min(x + new_w, width)          # Конец по X (не больше ширины)
            end_y = min(y + new_h, height)         # Конец по Y (не больше высоты)
            
            # Вычисляем фактические размеры видимой области
            w = end_x - start_x
            h = end_y - start_y

            # Пропускаем если царапина полностью за границами изображения
            if w <= 0 or h <= 0:
                continue

            # Вычисляем какую часть царапины мы используем
            # Смещение внутри исходной царапины (если часть царапины за границами)
            scratch_start_x = max(0, -x)  # Если x отрицательный - начинаем не с начала царапины
            scratch_start_y = max(0, -y)  # Если y отрицательный - начинаем не с начала царапины
            
            # Конечные координаты в исходной царапине
            scratch_end_x = scratch_start_x + w
            scratch_end_y = scratch_start_y + h

            # Обрезаем царапину до видимой части
            # Берем только ту часть царапины, которая попадает на изображение
            visible_scratch_rgb = scratch_rgb[scratch_start_y:scratch_end_y, scratch_start_x:scratch_end_x]
            visible_scratch_alpha = scratch_alpha_3c[scratch_start_y:scratch_end_y, scratch_start_x:scratch_end_x]

            # Выделяем область интереса (ROI) на целевом изображении
            # Это та область, куда будет наложена видимая часть царапины
            roi = overlay[start_y:end_y, start_x:end_x]

            # Смешиваем царапину с исходным изображением
            # Формула альфа-смешивания: результат = царапина * прозрачность + фон * (1 - прозрачность)
            blended = (visible_scratch_rgb * visible_scratch_alpha + roi * (1 - visible_scratch_alpha)).astype(np.uint8)

            # Заменяем область на исходном изображении смешанным результатом
            overlay[start_y:end_y, start_x:end_x] = blended

    # Возвращаем изображение с наложенными царапинами
    return overlay