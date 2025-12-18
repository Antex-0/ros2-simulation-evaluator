import os
import zipfile
import subprocess
import json
import shutil
import xml.etree.ElementTree as ET
import sys

def extract_zip(zip_path, extract_to):
    """
    Extracts the contents of a zip file to a target directory.

    :param zip_path: Path to the uploaded zip file.
    :param extract_to: Folder where files should be extracted.
    :return: The path to the package root or None if failed.
    """
    # ... existing code ...
    # 1. Clean up previous extraction to ensure fresh start
    if os.path.exists(extract_to):
        try:
            shutil.rmtree(extract_to)
        except:
            pass
    
    # 2. Verify source file exists
    if not os.path.exists(zip_path):
        return f"Error: The file '{zip_path}' was not found."

    # 3. Extract
    try:
        os.makedirs(extract_to)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except Exception as e:
        return f"Zip Extraction Failed: {str(e)}"

    # 4. Find package root
    for root, dirs, files in os.walk(extract_to):
        if "package.xml" in files:
            return root
    return "Error: Extracted zip, but no package.xml found."

def check_structure(package_root):
    report = {"passed": False, "errors": [], "files_found": []}
    
    # List files for debugging
    try:
        report["files_found"] = os.listdir(package_root)
    except:
        pass

    # Check setup.py (Case Insensitive)
    # This allows 'setup.py', 'Setup.py', 'SETUP.PY'
    has_setup = any(f.lower() == "setup.py" for f in report["files_found"])

    if has_setup:
        report["passed"] = True
    else:
        report["passed"] = False
        report["errors"].append(f"Missing setup.py. Found: {report['files_found']}")

    return report

def check_code_quality(package_root):
    results = {"syntax_errors": [], "safety_warnings": []}
    
    for root, dirs, files in os.walk(package_root):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                
                # Run Flake8
                cmd = [sys.executable, "-m", "flake8", file_path, "--select=E9,F63,F7", "--format=default"]
                try:
                    proc = subprocess.run(cmd, capture_output=True, text=True)
                    if proc.stdout:
                        results["syntax_errors"].append(f"{file}: {proc.stdout.strip()}")
                except:
                    pass

                # Run Safety Check
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                        if "while True" in content or "while(1)" in content:
                            if "sleep" not in content:
                                results["safety_warnings"].append(f"{file}: Infinite loop detected without sleep.")
                except:
                    pass
    return results

if __name__ == "__main__":
    # 1. Determine which file to check
    # If app.py sends a filename argument, use it. Otherwise default.
    if len(sys.argv) > 1:
        zip_file = sys.argv[1]
    else:
        zip_file = "test_upload.zip"

    # 2. Extract to a temp folder (outside workspace to prevent Flask reload loops)
    extract_folder = "/tmp/ros_extraction"
    
    pkg_root = extract_zip(zip_file, extract_folder)
    
    final_report = {
        "structure": {"passed": False, "errors": []},
        "code_quality": {"syntax_errors": [], "safety_warnings": []}
    }

    # 3. Run Checks
    if isinstance(pkg_root, str) and not os.path.isdir(pkg_root):
        # If extract_zip returned an error string
        final_report["structure"]["errors"].append(pkg_root)
    else:
        # Success
        final_report["structure"] = check_structure(pkg_root)
        if final_report["structure"]["passed"]:
            final_report["code_quality"] = check_code_quality(pkg_root)

    # 4. Save Report
    print(json.dumps(final_report, indent=4))
    with open("report.json", "w") as f:
        json.dump(final_report, f, indent=4)