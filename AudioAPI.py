# Flask application code in AudioAPI.py
import os
from parselmouth.praat import run_file
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import voiceAnalyser.voice as mysp


# 
# Flask application setup
app = Flask(__name__)

# Set the base directory where AudioAPI.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory for uploaded files within the 'myprosody/dataset' folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'myprosody', 'dataset', 'audioFiles', '')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class VoiceAnalysisResults:
    def __init__(self):
        self.syllables = None
        self.pauses = None
        self.speech_rate = None
        self.articulation_rate = None
        self.speaking_duration = None
        self.original_duration = None
        self.balance = None
        self.f0_mean = None
        self.f0_std = None
        self.f0_median = None
        self.f0_min = None
        self.f0_max = None
        self.f0_quantile25 = None
        self.f0_quantile75 = None
        self.pronunciation_score_percentage = None
        self.gender_analysis_result = None
        self.total_speech_analysis_results = None 
        # self.prosody_analysis_results = None
        # self.speech_lev_results = None  # Added for mysplev results
        self.error = None

    def to_dict(self):
        # Convert all attributes to a dictionary
        return {attr: getattr(self, attr) for attr in self.__dict__}



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
        voice_analysis = VoiceAnalysisResults()

        # voice_analysis.syllables = mysp.myspsyl(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.pauses = mysp.mysppaus(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.speech_rate = mysp.myspsr(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.articulation_rate = mysp.myspatc(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.speaking_duration = mysp.myspst(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.original_duration = mysp.myspod(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.balance = mysp.myspbala(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.f0_mean = mysp.myspf0mean(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.f0_std = mysp.myspf0sd(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.f0_median = mysp.myspf0med(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.f0_min = mysp.myspf0min(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.f0_max = mysp.myspf0max(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.f0_quantile25 = mysp.myspf0q25(filename_wo_ext, UPLOAD_FOLDER)
        # voice_analysis.f0_quantile75 = mysp.myspf0q75(filename_wo_ext, UPLOAD_FOLDER)
        voice_analysis.pronunciation_score_percentage = mysp.mysppron(filename_wo_ext, UPLOAD_FOLDER)
        voice_analysis.gender_analysis_result = mysp.myspgend(filename_wo_ext, UPLOAD_FOLDER)
        voice_analysis.total_speech_analysis_results = mysp.mysptotal(filename_wo_ext, UPLOAD_FOLDER)

        # voice_analysis.prosody_analysis_results = mysp.myprosody(filename_wo_ext, UPLOAD_FOLDER) 
        # voice_analysis.speech_lev_results = mysp.mysplev(filename_wo_ext, UPLOAD_FOLDER)



        # Check for errors in any of the results
        for attr, value in voice_analysis.to_dict().items():
            if isinstance(value, dict) and 'error' in value:
                voice_analysis.error = value['error']
                break

        # If an error occurred in any function, return the error
        if voice_analysis.error is not None:
            return jsonify({"error": voice_analysis.error}), 500

        # Return the structured results as JSON
        return jsonify(voice_analysis.to_dict()), 200
    except Exception as e:
        app.logger.error(f"An error occurred during ML processing: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8000)
    app.run(debug=True)