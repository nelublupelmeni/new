import os
import cv2
from flask import Flask, render_template, request, send_from_directory
from effects import apply_noise, apply_sepia

# Базовая директория проекта (на уровень выше scripts/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пути
UPLOAD_FOLDER = os.path.join(BASE_DIR, "test_photos")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "templates")

# Создаём папки, если их нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Flask-приложение
app = Flask(__name__, template_folder=TEMPLATES_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            # Сохраняем загруженное фото
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Загружаем картинку через OpenCV
            img = cv2.imread(filepath)

            # Применяем эффекты (шум + сепия)
            img = apply_noise(img, intensity=30)
            img = apply_sepia(img, strength=0.8)

            # Сохраняем результат
            output_filename = "processed_" + file.filename
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            cv2.imwrite(output_path, img)

            # Передаём пути в шаблон
            return render_template(
                "result.html",
                original=file.filename,
                processed=output_filename
            )
    return render_template("index.html")

@app.route("/test_photos/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/output/<filename>")
def processed_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
