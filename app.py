import os
import cv2
import numpy as np
from flask import Flask, render_template, request, send_file, url_for, session, jsonify
from werkzeug.utils import secure_filename
import uuid

from effects.sepia import add_sepia
from effects.scratchers import add_scratches
from effects.noise import add_noise

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Создаем папки если их нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_path, effects_config):
    """
    Основная функция обработки изображения
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Не удалось загрузить изображение")
    
    # Применяем эффекты
    if effects_config.get('sepia_strength', 0) > 0:
        image = add_sepia(image, effects_config['sepia_strength'])
    
    if effects_config.get('noise_intensity', 0) > 0:
        image = add_noise(image, effects_config['noise_intensity'])
    
    if effects_config.get('scratches_density', 0) > 0:
        image = add_scratches(
            image,
            scratch_folder='scratches',
            alpha=effects_config.get('scratches_alpha', 0.5),
            density=effects_config.get('scratches_density', 5),
            size_range=effects_config.get('scratches_size', (0.1, 0.3)),
            rotation_range=effects_config.get('scratches_rotation', (-180, 180))
        )
    
    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return render_template('index.html', error='Файлы не выбраны')
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    for file in files:
        if file and file.filename != '' and allowed_file(file.filename):
            # Генерируем уникальное имя файла
            file_id = str(uuid.uuid4())
            filename = f"{file_id}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            uploaded_files.append({
                'id': file_id,
                'filename': filename,
                'original_name': file.filename,
                'url': url_for('static', filename=f'uploads/{filename}')
            })
    
    if not uploaded_files:
        return render_template('index.html', error='Не удалось загрузить файлы')
    
    # Сохраняем информацию о файлах в сессии
    session['uploaded_files'] = uploaded_files
    session['current_file_index'] = 0
    
    return render_template('editor.html', files=uploaded_files, current_index=0)

@app.route('/editor')
def editor():
    uploaded_files = session.get('uploaded_files', [])
    if not uploaded_files:
        return render_template('index.html', error='Сначала загрузите фотографии')
    
    current_index = session.get('current_file_index', 0)
    return render_template('editor.html', files=uploaded_files, current_index=current_index)

@app.route('/process', methods=['POST'])
def process_current_image():
    data = request.get_json()
    effects_config = data.get('effects', {})
    file_index = data.get('file_index', 0)
    
    uploaded_files = session.get('uploaded_files', [])
    if not uploaded_files or file_index >= len(uploaded_files):
        return jsonify({'error': 'Файл не найден'}), 404
    
    current_file = uploaded_files[file_index]
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], current_file['filename'])
    
    try:
        # Обрабатываем изображение
        processed_image = process_image(original_path, effects_config)
        
        # Сохраняем результат
        result_filename = f"processed_{current_file['filename']}"
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
        cv2.imwrite(result_path, processed_image)
        
        # Обновляем информацию о файле
        current_file['processed_url'] = url_for('static', filename=f'uploads/{result_filename}')
        current_file['processed_filename'] = result_filename
        session['uploaded_files'] = uploaded_files
        
        return jsonify({
            'success': True,
            'processed_url': current_file['processed_url']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    uploaded_files = session.get('uploaded_files', [])
    for file_info in uploaded_files:
        if file_info['id'] == file_id and 'processed_filename' in file_info:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info['processed_filename'])
            return send_file(file_path, as_attachment=True, download_name=f"vintage_{file_info['original_name']}")
    
    return "Файл не найден", 404

@app.route('/download_all')
def download_all():
    # Здесь можно реализовать скачивание всех обработанных файлов в zip-архиве
    pass

@app.route('/reset')
def reset():
    session.clear()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)