from flask import Flask, request, jsonify
import json
import os
import requests
app = Flask(__name__)
# GitHub Credentials (Replace with your details)
GITHUB_USERNAME = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
GITHUB_TOKEN = "your-github-personal-access-token"
GITHUB_FILE_PATH = "csi_data.json"
def upload_to_github(data):
    """ Upload CSI data to GitHub as JSON """
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Get the existing file SHA (needed for updates)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        sha = None
    # Convert data to JSON format
    json_data = json.dumps(data, indent=4)
    # Prepare the payload
    payload = {
        "message": "Update CSI data",
        "content": json_data.encode("utf-8").hex(),  # Encode data to hex
        "sha": sha  # Required if updating existing file
    }
    # Upload to GitHub
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code
@app.route('/upload', methods=['POST'])
def upload():
    """ Receive CSI data from ESP32 and upload it to GitHub """
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
    # Upload to GitHub
    status = upload_to_github(data)
    if status == 200 or status == 201:
        return jsonify({"status": "success", "message": "CSI data saved to GitHub"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)






