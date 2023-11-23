# Flask application code in AudioAPI.py
import os
from parselmouth.praat import run_file
from flask import Flask, request
from werkzeug.utils import secure_filename
import voiceAnalyser.voice as mysp



# Flask application setup
app = Flask(__name__)

# Set the base directory where AudioAPI.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory for uploaded files within the 'myprosody/dataset' folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'myprosody', 'dataset', 'audioFiles', '')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return 'No audio file part', 400

    file = request.files['audio']
    if file.filename == '':
        return 'No selected file', 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    filename_wo_ext = os.path.splitext(filename)[0]

    try:
        result = mysp.myspgend(filename_wo_ext, UPLOAD_FOLDER)
        if result is None:
            return "The ML function did not return any result.", 500

        return {"result": result}, 200
    except Exception as e:
        app.logger.error(f"An error occurred during ML processing: {e}")
        return f"An error occurred during ML processing: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
