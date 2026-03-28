from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from image_recognition_model import recognize_plant

app = Flask(__name__)
CORS(app)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        file.save(tmp.name)
        try:
            result = recognize_plant(tmp.name)
        finally:
            os.unlink(tmp.name)
    
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

def _debug_mode() -> bool:
    v = os.environ.get('FLASK_DEBUG', 'true').strip().lower()
    return v in ('1', 'true', 'yes')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=_debug_mode())
