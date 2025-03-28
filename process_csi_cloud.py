
import requests
import base64
import json
import math
#import datetime
from datetime import datetime

from math import sqrt, atan2
import os

# ========== GitHub Setup ==========
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set this in Render env
GITHUB_USER = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
INPUT_FILE_PATH = "csi_data/raw_csi_data.txt"
#OUTPUT_FILE_PATH = "csi_data/processed_output.txt"

now = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE_PATH = f"csi_data/processed_output_{now}.txt"


HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"

# ========== CSI Processing Logic ==========
def unwrap_phase(current_phase, next_phase):
    delta = next_phase - current_phase
    if delta > math.pi:
        return current_phase + delta - (2 * math.pi)
    elif delta < -math.pi:
        return current_phase + delta + (2 * math.pi)
    return next_phase

def phase_filter_linear_fit(phases):
    F = 63
    if len(phases) <= F:
        return
    alpha_1 = (phases[F] - phases[0]) / (2 * math.pi * F)
    alpha_0 = sum(phases[:F]) / F
    for i in range(len(phases)):
        phases[i] = phases[i] - ((alpha_1 * i) + alpha_0)

# ========== GitHub Functions ==========
def get_file_from_github(filepath):
    print(f"📥 Fetching: {filepath}")
    url = f"{API_URL}/{filepath}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        content = base64.b64decode(res.json()["content"]).decode()
        sha = res.json()["sha"]
        return content, sha
    else:
        print(f"❌ Could not fetch file: {res.status_code}")
        return None, None

# def upload_file_to_github(content_str, path, sha=None):
#     print(f"📤 Uploading to: {path}")
#     url = f"{API_URL}/{path}"
#     payload = {
#         "message": "Upload processed CSI output",
#         "content": base64.b64encode(content_str.encode()).decode(),
#         "sha": sha
#     }
#     res = requests.put(url, headers=HEADERS, json=payload)
#     if res.status_code in [200, 201]:
#         print("✅ Upload complete.")
#     else:
#         print(f"❌ Upload failed: {res.status_code}")
#         print(res.text)

# def upload_file_to_github(content_str, path, sha=None):
#     print(f"📤 Uploading to: {path}")
#     url = f"{API_URL}/{path}"

#     payload = {
#         "message": "Upload processed CSI output",
#         "content": base64.b64encode(content_str.encode()).decode()
#     }

#     if sha:
#         payload["sha"] = sha  # Only add if it exists

#     res = requests.put(url, headers=HEADERS, json=payload)

#     if res.status_code in [200, 201]:
#         print("✅ Upload complete.")
#     else:
#         print(f"❌ Upload failed: {res.status_code}")
#         print(res.text)

# def upload_file_to_github(content_str, path, sha=None):
#     print(f"📤 Uploading to: {path}")
#     url = f"{API_URL}/{path}"

#     payload = {
#         "message": "Upload processed CSI output",
#         "content": base64.b64encode(content_str.encode()).decode()
#     }

#     # ✅ Only include SHA if it is a real string
#     if sha is not None and isinstance(sha, str):
#         payload["sha"] = sha

#     res = requests.put(url, headers=HEADERS, json=payload)

#     if res.status_code in [200, 201]:
#         print("✅ Upload complete.")
#     else:
#         print(f"❌ Upload failed: {res.status_code}")
#         print(res.text)

# def upload_file_to_github(content_str, path):
#     print(f"📤 Uploading new file to: {path}")
#     url = f"{API_URL}/{path}"

#     payload = {
#         "message": "Create new processed CSI file",
#         "content": base64.b64encode(content_str.encode()).decode()
#     }

#     res = requests.put(url, headers=HEADERS, json=payload)

#     if res.status_code in [200, 201]:
#         print("✅ Upload complete.")
#     else:
#         print(f"❌ Upload failed: {res.status_code}")
#         print(res.text)

# def upload_file_to_github(content_str, path):
#     print(f"📤 Uploading to: {path}")
#     url = f"{API_URL}/{path}"

#     # Get SHA if the file exists
#     res = requests.get(url, headers=HEADERS)
#     sha = None
#     if res.status_code == 200:
#         sha = res.json().get("sha")
#         print(f"✅ Found existing file. SHA: {sha}")
#     elif res.status_code == 404:
#         print("📁 File does not exist. A new one will be created.")
#     else:
#         print(f"❌ Failed to check file. Status: {res.status_code}")
#         return

#     # Create payload
#     payload = {
#         "message": "Upload processed CSI output",
#         "content": base64.b64encode(content_str.encode()).decode()
#     }
#     if sha:
#         payload["sha"] = sha

#     # Send PUT request
#     put_res = requests.put(url, headers=HEADERS, json=payload)
#     if put_res.status_code in [200, 201]:
#         print("✅ Upload success!")
#     else:
#         print(f"❌ Upload failed. Status: {put_res.status_code}")
#         print(put_res.text)

# def upload_file_to_github(content_str, path):
#     print(f"📤 Uploading to: {path}")
#     url = f"{API_URL}/{path}"

#     # Step 1: Check if file exists to get SHA
#     res = requests.get(url, headers=HEADERS)
#     sha = None

#     if res.status_code == 200:
#         sha = res.json().get("sha", None)
#         print(f"✅ File exists. SHA: {sha}")
#     elif res.status_code == 404:
#         print("📁 File not found. Creating new one.")
#     else:
#         print(f"❌ Error checking file: {res.status_code}")
#         print(res.text)
#         return

#     # Step 2: Build payload
#     payload = {
#         "message": "Upload processed CSI output",
#         "content": base64.b64encode(content_str.encode()).decode()
#     }

#     # ✅ Only include SHA if it’s a valid string
#     if sha:
#         payload["sha"] = sha

#     # Step 3: Upload file
#     put = requests.put(url, headers=HEADERS, json=payload)

#     if put.status_code in [200, 201]:
#         print("✅ Upload successful.")
#     else:
#         print(f"❌ Upload failed: {put.status_code}")
#         print(put.text)

def upload_file_to_github(content_str, path):
    print(f"📤 Uploading to: {path}")
    url = f"{API_URL}/{path}"

    # Step 1: Get SHA of the existing file (if any)
    sha = None
    res = requests.get(url, headers=HEADERS)
    
    if res.status_code == 200:
        sha = res.json().get("sha")
        print(f"✅ Existing file found. SHA: {sha}")
    elif res.status_code == 404:
        print("📁 File does not exist yet. Will be created.")
    else:
        print(f"❌ Failed to check file. Status: {res.status_code}")
        print(res.text)
        return

    # Step 2: Prepare upload payload
    payload = {
        "message": "Update processed CSI data",
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    }

    # 🔐 Add SHA only if it exists
    if sha is not None:
        payload["sha"] = sha

    # Step 3: Upload to GitHub
    put_response = requests.put(url, headers=HEADERS, json=payload)

    print(f"📤 GitHub Response: {put_response.status_code}")
    print(put_response.text)

    if put_response.status_code in [200, 201]:
        print("✅ File uploaded successfully.")
    else:
        print("❌ File upload failed.")


# ========== CSI Parsing + Processing ==========
def process_csi(raw_text):
    print("🧠 Processing CSI...")
    lines = raw_text.strip().splitlines()
    output = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith("Timestamp:"):
            i += 1
            continue
        timestamp = lines[i].strip()
        i += 1
        if i >= len(lines) or not lines[i].startswith("CSI Data:"):
            continue
        csi_line = lines[i].replace("CSI Data:", "").strip()
        i += 1

        tokens = csi_line.split()
        if len(tokens) % 2 != 0:
            continue

        imaginary, real = [], []
        for j in range(0, len(tokens), 2):
            imaginary.append(int(tokens[j]))
            real.append(int(tokens[j+1]))

        amplitudes = [sqrt(im**2 + re**2) for im, re in zip(imaginary, real)]
        phases = [atan2(im, re) for im, re in zip(imaginary, real)]

        for j in range(len(phases) - 1):
            phases[j+1] = unwrap_phase(phases[j], phases[j+1])
        if len(phases) >= 64:
            phase_filter_linear_fit(phases)

        #ts_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # timestamp = lines[i].strip().replace("Timestamp:", "").strip() 
        # i += 1

        output.append(f"{timestamp}")
        #output.append("Amplitude: " + ", ".join(f"{x:.4f}" for x in amplitudes))
        output.append("Amplitude: " + ", ".join(str(x) for x in amplitudes))

        output.append("Phase: " + ", ".join(f"{x:.4f}" for x in phases))
        output.append("")

        #output.append(f"{timestamp} | {ts_now}")
        # timestamp_line = lines[i].strip()
        # timestamp = timestamp_line.split(":", 1)[1].strip() if "Timestamp:" in timestamp_line else ""
        # i += 1

        # output.append(f"{timestamp}")

        # output.append("Amplitude: " + ", ".join(f"{x:.2f}" for x in amplitudes))
        # output.append("Phase: " + ", ".join(f"{x:.4f}" for x in phases))
        # output.append("")

    return "\n".join(output)

# ========== Main ==========

if __name__ == "__main__":
    raw_text, sha = get_file_from_github(INPUT_FILE_PATH)
    if raw_text:
        processed = process_csi(raw_text)
       # upload_file_to_github(processed, OUTPUT_FILE_PATH)
       # upload_file_to_github(processed_data, "csi_data/processed_output.txt")
        upload_file_to_github(processed, "csi_data/processed_output.txt")

