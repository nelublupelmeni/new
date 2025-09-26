import os
from flask import Flask, render_template, request, send_from_directory, send_file
from effects import process_image_dynamic
from io import BytesIO
import cv2

# Базовая директория проекта
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
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            filename = file.filename
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(input_path)
            
            # Обработка по умолчанию (статическая)
            output_filename = f"final_{filename}"
            process_image_dynamic(
                input_path=input_path,
                output_folder=OUTPUT_FOLDER,
                scratch_path=SCRATCH_PATH,
                sepia=0.8,
                noise=30,
                scratch_alpha=0.6
            )
            
            return render_template(
                "result.html",
                original=filename,
                processed=output_filename
            )
    return render_template("index.html")


@app.route("/output/<filename>")
def processed_file(filename):
    """
    Динамическая обработка изображения с параметрами ползунков.
    Параметры: sepia, noise, scratch (0-100)
    """
    sepia = float(request.args.get("sepia", 80)) / 100
    noise = float(request.args.get("noise", 30))
    scratch_alpha = float(request.args.get("scratch", 60)) / 100

    input_path = os.path.join(UPLOAD_FOLDER, filename.replace("final_", ""))
    if not os.path.exists(input_path):
        return "Файл не найден", 404

    # Генерация изображения в памяти
    img = process_image_dynamic(
        input_path=input_path,
        output_folder=None,  # Не сохраняем
        scratch_path=SCRATCH_PATH,
        sepia=sepia,
        noise=noise,
        scratch_alpha=scratch_alpha
    )

    # Конвертируем в байты для отправки клиенту
    _, buffer = cv2.imencode(".jpg", img)
    return send_file(BytesIO(buffer.tobytes()), mimetype="image/jpeg")


@app.route("/test_photos/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)
