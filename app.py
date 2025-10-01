from flask import Flask, render_template, request, send_file, jsonify
import tempfile
import os
import base64
from io import BytesIO
from process import process_image, create_preview
import atexit
from PIL import Image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file

# Список для отслеживания временных файлов
temp_files = []

def cleanup_temp_files():
    """Очистка временных файлов при завершении работы"""
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Error deleting temp file {temp_file}: {e}")

# Регистрируем очистку при выходе
atexit.register(cleanup_temp_files)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        # Получение файла и параметров
        file = request.files['image']
        params = request.form
        
        # Обработка изображения
        processed_image = process_image(file, params)
        
        if processed_image is None:
            return jsonify({'error': 'Неверный формат изображения'}), 400
        
        # Сохранение в временный файл
        _, temp_filename = tempfile.mkstemp(suffix='.jpg')
        processed_image.save(temp_filename, format='JPEG', quality=95)
        temp_files.append(temp_filename)  # Добавляем в список для очистки
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(temp_filename)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview', methods=['POST'])
def preview():
    """Эндпоинт для быстрого предпросмотра"""
    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'error': 'No image provided'}), 400
            
        params = request.form
        
        # Создаем превью (уменьшенное изображение для скорости)
        preview_data = create_preview(file, params)
        
        if preview_data:
            # Конвертируем в base64 для отправки в HTML
            buffered = BytesIO()
            preview_data.save(buffered, format="JPEG", quality=70)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return jsonify({
                'success': True,
                'preview': f"data:image/jpeg;base64,{img_str}"
            })
        else:
            return jsonify({'error': 'Preview generation failed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    """Скачивание обработанного изображения с поддержкой разных форматов и качества"""
    try:
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        if not os.path.exists(temp_path):
            return "File not found", 404

        # Получаем параметры формата и качества из запроса
        format = request.args.get('format', 'jpg')
        quality = request.args.get('quality', 'high')
        
        # Определяем качество для JPEG/WebP
        quality_map = {
            'low': 30,
            'medium': 70,
            'high': 95
        }
        
        quality_value = quality_map.get(quality, 95)
        
        # Определяем MIME type и расширение
        format_map = {
            'jpg': ('image/jpeg', 'jpg'),
            'jpeg': ('image/jpeg', 'jpg'),
            'png': ('image/png', 'png'),
            'webp': ('image/webp', 'webp')
        }
        
        mime_type, extension = format_map.get(format, ('image/jpeg', 'jpg'))
        
        # Открываем исходное изображение
        img = Image.open(temp_path)
        
        # Конвертируем в RGB если нужно для JPEG
        if format in ('jpg', 'jpeg') and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Создаем буфер для выходного изображения
        output_buffer = BytesIO()
        
        # Сохраняем в выбранном формате с нужным качеством
        if format in ('jpg', 'jpeg'):
            img.save(output_buffer, format='JPEG', quality=quality_value, optimize=True)
        elif format == 'png':
            img.save(output_buffer, format='PNG', optimize=True)
        elif format == 'webp':
            img.save(output_buffer, format='WEBP', quality=quality_value, method=6)
        else:
            # По умолчанию сохраняем как JPEG
            img.save(output_buffer, format='JPEG', quality=quality_value, optimize=True)
        
        output_buffer.seek(0)
        
        # Создаем имя файла для скачивания
        download_name = f"aged_photo.{extension}"
        
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name=download_name,
            mimetype=mime_type
        )
        
    except Exception as e:
        return jsonify({'error': f'Error processing download: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Ручная очистка временных файлов"""
    try:
        cleanup_temp_files()
        temp_files.clear()
        return jsonify({'success': True, 'message': 'Temporary files cleaned up'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)