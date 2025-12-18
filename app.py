import os
import subprocess
import json
import sys
from flask import Flask, render_template, request, jsonify

# template_folder="." makes it look in the current folder for index.html
app = Flask(__name__, template_folder=".")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"})
    
    # 1. FORCE DELETE OLD FILE
    # This guarantees we don't accidentally check an old file
    zip_name = "user_upload.zip"
    if os.path.exists(zip_name):
        try:
            os.remove(zip_name)
        except:
            pass
    
    # 2. SAVE NEW FILE
    file.save(zip_name)
    
    try:
        # 3. RUN CHECKER (Passing the specific filename)
        result = subprocess.run(
            [sys.executable, "checker.py", zip_name], 
            capture_output=True, 
            text=True
        )
        
        # 4. RETURN REPORT
        if os.path.exists("report.json"):
            with open("report.json", "r") as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"error": "No report found", "logs": result.stdout})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/run_sim", methods=["POST"])
def run_sim():
    try:
        # Run the runner script
        result = subprocess.run([sys.executable, "runner.py"], capture_output=True, text=True)
        
        log = "No logs."
        if os.path.exists("simulation_log.txt"):
            with open("simulation_log.txt", "r") as f:
                log = f.read()
                
        return jsonify({"status": "Done", "logs": log})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)