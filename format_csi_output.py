import requests
import base64
import os
import re
import time  # ⏳ Needed for retry delay

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
INPUT_FILE_PATH = "csi_data/processed_output.txt"
OUTPUT_FILE_PATH = "csi_data/formatted_output.csv"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file(filepath):
    url = f"{API_URL}/{filepath}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        try:
            return base64.b64decode(res.json()["content"]).decode(), res.json().get("sha")
        except KeyError:
            download_url = res.json().get("download_url")
            if download_url:
                return requests.get(download_url).text, res.json().get("sha")
    return None, None

def upload_file(content_str, path):
    url = f"{API_URL}/{path}"
    sha = None
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        sha = res.json().get("sha")
    payload = {
        "message": "Upload formatted CSI output",
        "content": base64.b64encode(content_str.encode()).decode()
    }
    if sha:
        payload["sha"] = sha
    put_res = requests.put(url, headers=HEADERS, json=payload)
    print(f"🔁 GitHub Response: {put_res.status_code}")

def format_blocks(text):
    pattern = re.compile(r"^Timestamp:\s*(.*?)\nAmplitude: (.*?)\nPhase: (.*?)(?=\n\S|\Z)", re.DOTALL | re.MULTILINE)
    matches = pattern.findall(text)
    blocks = []
    for timestamp, amp_str, phase_str in matches:
        amplitudes = [float(a.strip()) for a in amp_str.strip().split(',')]
        phases = [float(p.strip()) for p in phase_str.strip().split(',')]
        blocks.append(f"{timestamp}\n{amplitudes}\n{phases}\n\n")
    return ''.join(blocks)

if __name__ == "__main__":
    print("🚀 format_csi_output.py is running...")
    for attempt in range(10):
        print(f"⏳ Attempt {attempt+1}")
        text, _ = get_file(INPUT_FILE_PATH)
        if text:
            print("✅ File fetched. Formatting...")
            formatted = format_blocks(text)
            upload_file(formatted, OUTPUT_FILE_PATH)
            break
        print("❌ Not ready, retrying...")
        time.sleep(4)
