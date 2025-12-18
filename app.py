import os
import subprocess
import json
import sys
from flask import Flask, render_template, request, jsonify

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
    
    # Force clean up old files
    zip_name = "user_upload.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    if os.path.exists("simulation_log.txt"):
        os.remove("simulation_log.txt")

    file.save(zip_name)
    
    try:
        # Run checker
        result = subprocess.run(
            [sys.executable, "checker.py", zip_name], 
            capture_output=True, 
            text=True
        )
        
        if os.path.exists("report.json"):
            with open("report.json", "r") as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"error": "No report found", "details": result.stdout})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/run_sim", methods=["POST"])
def run_sim():
    try:
        # 1. Find the extracted node file
        # The checker extracts files to /tmp/ros_extraction. We need to find the python script there.
        extract_path = "/tmp/ros_extraction"
        node_file = None
        
        if os.path.exists(extract_path):
            for root, dirs, files in os.walk(extract_path):
                for f in files:
                    if f.endswith(".py") and f != "setup.py":
                        node_file = os.path.join(root, f)
                        break
                if node_file: break
        
        if not node_file:
            return jsonify({"error": "No Python node found in extracted package."})

        # 2. Run runner.py with the node file argument
        result = subprocess.run(
            [sys.executable, "runner.py", node_file],
            capture_output=True,
            text=True
        )
        
        # 3. Read logs
        log_content = "No logs generated."
        if os.path.exists("simulation_log.txt"):
            with open("simulation_log.txt", "r") as f:
                log_content = f.read()
                
        return jsonify({"status": "Done", "logs": log_content})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)