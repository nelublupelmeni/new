import cv2
import numpy as np
import os

def add_noise(image, intensity=25):
    noisy = image.astype(np.float32)
    noise = np.random.normal(0, intensity, image.shape).astype(np.float32)
    noisy += noise
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

def add_sepia(image, strength=0.8):
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia_img = cv2.transform(image, sepia_filter)
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    output = cv2.addWeighted(image, 1 - strength, sepia_img, strength, 0)
    return output

def add_textures(image, scratch_path, alpha):
    textures = cv2.imread(scratch_path, cv2.IMREAD_UNCHANGED)
    if textures is None:
        return image
    textures = cv2.resize(textures, (image.shape[1], image.shape[0]))
    scratch_rgb = textures[:, :, :3]
    scratch_alpha = textures[:, :, 3] / 255.0
    scratch_alpha = np.clip(scratch_alpha * alpha, 0, 1)
    scratch_alpha_3c = cv2.merge([scratch_alpha, scratch_alpha, scratch_alpha])
    overlay = (scratch_rgb * scratch_alpha_3c + image * (1 - scratch_alpha_3c)).astype(np.uint8)
    return overlay

def process_image_dynamic(input_path, output_folder="output", scratch_path=None,
                          sepia=0.8, noise=30, scratch_alpha=0.6):
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Изображение не найдено: {input_path}")

    # Применяем эффекты по параметрам
    if noise > 0:
        img = add_noise(img, intensity=noise)
    if sepia > 0:
        img = add_sepia(img, strength=sepia)
    if scratch_path and scratch_alpha > 0:
        img = add_textures(img, scratch_path, alpha=scratch_alpha)

    # Если указан output_folder, сохраняем
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_folder, f"final_{filename}")
        cv2.imwrite(output_path, img)

    return img
