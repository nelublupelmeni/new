from flask import Flask, render_template, request, send_file, jsonify
import tempfile
import os
from process import process_image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        file = request.files['image']
        params = request.form
        
        processed_image = process_image(file, params)
        
        if processed_image is None:
            return jsonify({'error': 'Неверный формат изображения'}), 400
        
        _, temp_filename = tempfile.mkstemp(suffix='.jpg')
        processed_image.save(temp_filename)
        
        return jsonify({
            'success': True,
            'filename': os.path.basename(temp_filename)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    return send_file(temp_path, as_attachment=True, download_name='aged_photo.jpg')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)