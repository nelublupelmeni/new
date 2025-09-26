import os
import cv2
from flask import Flask, render_template, request, send_from_directory
from effects import process_image

#ДОБАВИТЬ ЧТЕНИЕ РУССКИХ ПУТЕЙ

# Базовая директория проекта (на уровень выше scripts/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пути
UPLOAD_FOLDER = os.path.join(BASE_DIR, "test_photos","uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "test_photos","output")
TEMPLATES_FOLDER = os.path.join(BASE_DIR, "templates")
SCRATCH_PATH = os.path.join(BASE_DIR, "scratches", "scratches-png-37699.png")

# Создаём папки, если их нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Flask-приложение
app = Flask(__name__, template_folder=TEMPLATES_FOLDER)

@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            # Сохраняем загруженный файл
            filename = file.filename
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(input_path)
            
            # Обрабатываем изображение
            output_filename = f"final_{filename}"
            process_image(
                input_path=input_path,
                output_folder=OUTPUT_FOLDER,
                scratch_path=SCRATCH_PATH
            )
            
            # Передаём пути в шаблон
            return render_template(
                "result.html",
                original=filename,
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