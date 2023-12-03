import os
import traceback
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pydub import AudioSegment  # Import AudioSegment from pydub
import voiceAnalyser.voice as mysp

# Flask application setup
app = Flask(__name__)

# Set the base directory where AudioAPI.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory for uploaded files within the 'myprosody/dataset' folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'myprosody', 'dataset', 'audioFiles', '')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class VoiceAnalysisResults:
    def __init__(self):
        self.total_speech_analysis_results = None 
        self.pronunciation_score_percentage = None
        self.gender_analysis_result = None
        self.error = None

    def to_dict(self):
        # Convert all attributes to a dictionary
        return {attr: getattr(self, attr) for attr in self.__dict__}

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        app.logger.warning("Audio part missing in request")
        return 'No audio file part', 400

    file = request.files['audio']
    if file.filename == '':
        app.logger.warning("No file selected for uploading")
        return 'No selected file', 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(file_path)

        # Convert M4A to WAV if necessary
        if file_path.endswith('.m4a'):
            m4a_audio = AudioSegment.from_file(file_path, format="m4a")
            wav_file_path = file_path.replace('.m4a', '.wav')
            m4a_audio.export(wav_file_path, format="wav")
            os.remove(file_path)  # Remove the original M4A file
            file_path = wav_file_path  # Update file_path to the new WAV file
        else:
            wav_file_path = file_path  # If file is not M4A, proceed with the original file

        filename_wo_ext = os.path.splitext(filename)[0].replace('.m4a', '')

        voice_analysis = VoiceAnalysisResults()
        
        # Perform voice analysis using external functions
        voice_analysis.total_speech_analysis_results = mysp.mysptotal(filename_wo_ext, UPLOAD_FOLDER)
        voice_analysis.pronunciation_score_percentage = mysp.mysppron(filename_wo_ext, UPLOAD_FOLDER)
        voice_analysis.gender_analysis_result = mysp.myspgend(filename_wo_ext, UPLOAD_FOLDER)
        
        # Check for errors in any of the results
        for value in voice_analysis.to_dict().items():
            if isinstance(value, dict) and 'error' in value:
                voice_analysis.error = value['error']
                break

        # If an error occurred in any function, return the error
        if voice_analysis.error is not None:
            app.logger.error(f"Error in voice analysis: {voice_analysis.error}")
            return jsonify({"error": voice_analysis.error}), 500

        # Return the structured results as JSON
        return jsonify(voice_analysis.to_dict()), 200
    except Exception as e:
        app.logger.error(f"An error occurred during voice analysis processing: {e}")
        traceback.print_exc()  # This will print the full traceback to the log
        return jsonify({"error": str(e)}), 500
    finally:
        # Delete the uploaded file after processing
        try:
            os.remove(wav_file_path)
            app.logger.info(f"Successfully deleted file: {wav_file_path}")

            textgrid_path = wav_file_path.replace('.wav', '.TextGrid')  # Assuming the audio file is a .wav file
            os.remove(textgrid_path)
            app.logger.info(f"Successfully deleted TextGrid file: {textgrid_path}")
            
        except Exception as e:
            app.logger.error(f"Failed to delete file: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
