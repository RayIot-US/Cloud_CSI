import requests
import base64
import os
import re

# GitHub Setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
INPUT_FILE_PATH = "csi_data/processed_output.txt"
# from datetime import datetime
# today = datetime.now().strftime("%Y%m%d")
# INPUT_FILE_PATH = f"csi_data/processed_output_{today}.txt"

OUTPUT_FILE_PATH = "csi_data/formatted_output.csv"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ========= GitHub Functions =========

# def get_file(filepath):
#     url = f"{API_URL}/{filepath}"
#     print(f"📥 Downloading: {filepath}")
#     res = requests.get(url, headers=HEADERS)
#     if res.status_code == 200:
#         content = base64.b64decode(res.json()["content"]).decode()
#         sha = res.json().get("sha")
#         return content, sha
#     else:
#         print(f"❌ Failed to fetch file. Status: {res.status_code}")
#         print(res.text)
#         return None, None

def get_file(filepath):
    url = f"{API_URL}/{filepath}"
    print(f"📥 Downloading: {filepath}")
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        json_data = res.json()
        try:
            # Try normal content decoding
            content = base64.b64decode(json_data["content"]).decode()
        except KeyError:
            # Fallback: GitHub doesn’t include content if the file is too large
            download_url = json_data.get("download_url")
            if not download_url:
                print("❌ No content or download_url found.")
                return None, None
            print("📡 Fetching large file from download_url...")
            download_res = requests.get(download_url)
            if download_res.status_code == 200:
                return download_res.text, json_data.get("sha")
            else:
                print("❌ Failed to fetch from download_url.")
                return None, None
        return content, json_data.get("sha")
    else:
        print(f"❌ Failed to fetch file. Status: {res.status_code}")
        print(res.text)
        return None, None


def upload_file(content_str, path):
    print(f"📤 Uploading to: {path}")
    url = f"{API_URL}/{path}"

    # Check if file exists to get SHA
    sha = None
    check = requests.get(url, headers=HEADERS)
    if check.status_code == 200:
        sha = check.json().get("sha")
        print(f"✅ Existing file SHA: {sha}")
    elif check.status_code == 404:
        print("📁 File not found — creating a new one.")
    else:
        print(f"❌ Failed to check file. Status: {check.status_code}")
        print(check.text)
        return

    payload = {
        "message": "Upload formatted CSI output",
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    }

    if sha:
        payload["sha"] = sha

    res = requests.put(url, headers=HEADERS, json=payload)
    print(f"🔁 GitHub Response: {res.status_code}")
    if res.status_code in [200, 201]:
        print("✅ Upload to GitHub successful.")
    else:
        print("❌ Upload failed.")
        print(res.text)

# ========= Formatter Logic =========

def format_blocks(text):
    #pattern = re.compile(r"^(.*?)\nTimestamp: r^(.*?)\nAmplitude: (.*?)\nPhase: (.*?)(?=\n\S|\Z)", re.DOTALL | re.MULTILINE)
    #pattern = re.compile(r"^(.*?)\nAmplitude: (.*?)\nPhase: (.*?)(?=\n\S|\Z)", re.DOTALL | re.MULTILINE)
    pattern = re.compile(r"^Timestamp:\s*(.*?)\nAmplitude: (.*?)\nPhase: (.*?)(?=\n\S|\Z)", re.DOTALL | re.MULTILINE)

    #pattern = re.compile(r"Timestamp: (.*?)\nAmplitude: (.*?)\nPhase: (.*?)(?=\nTimestamp:|\Z)", re.DOTALL)

    matches = pattern.findall(text)

    blocks = []
    for timestamp, amp_str, phase_str in matches:
        amplitudes = [float(a.strip()) for a in amp_str.strip().split(',')]
        phases = [float(p.strip()) for p in phase_str.strip().split(',')]
        block = f"{timestamp}\n{amplitudes}\n{phases}\n\n"
        blocks.append(block)

    return ''.join(blocks)

# ========= Main ==========

# if __name__ == "__main__":
#     text, _ = get_file(INPUT_FILE_PATH)
#     if text:
#         formatted_data = format_blocks(text)
#         upload_file(formatted_data, OUTPUT_FILE_PATH)

if __name__ == "__main__":
    print("🚀 format_csi_output.py is running...")
    text, _ = get_file(INPUT_FILE_PATH)
    if text:
        print("✅ File fetched. Starting formatting...")
        formatted_data = format_blocks(text)
        print("✅ Formatting complete. Sending to upload_file()...")
        upload_file(formatted_data, OUTPUT_FILE_PATH)
    else:
        print("❌ No input file content found.")


# import requests
# import base64
# import os
# import re

# # GitHub Setup
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# GITHUB_USER = "RayIot-US"
# GITHUB_REPO = "Cloud_CSI"
# INPUT_FILE_PATH = "csi_data/processed_output.txt"
# OUTPUT_FILE_PATH = "csi_data/formatted_output.csv"
# API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"

# HEADERS = {
#     "Authorization": f"token {GITHUB_TOKEN}",
#     "Accept": "application/vnd.github.v3+json"
# }

# # ========= GitHub Functions =========

# def get_file(filepath):
#     url = f"{API_URL}/{filepath}"
#     print(f"📥 Downloading: {filepath}")
#     res = requests.get(url, headers=HEADERS)
#     if res.status_code == 200:
#         content = base64.b64decode(res.json()["content"]).decode()
#         sha = res.json().get("sha")
#         return content, sha
#     else:
#         print(f"❌ Failed to fetch file. Status: {res.status_code}")
#         return None, None

# # def upload_file(content_str, path):
# #     print(f"📤 Uploading to: {path}")
# #     url = f"{API_URL}/{path}"

# #     # Check if file exists to get SHA
# #     sha = None
# #     check = requests.get(url, headers=HEADERS)
# #     if check.status_code == 200:
# #         sha = check.json().get("sha")

# #     payload = {
# #         "message": "Updated formatted CSI output",
# #         "content": base64.b64encode(content_str.encode()).decode()
# #     }

# #     if sha:
# #         payload["sha"] = sha


# #     else:
# #         print("📁 File not found — will create a new one.")


# #     res = requests.put(url, headers=HEADERS, json=payload)
# #     print(f"🔁 GitHub Response: {res.status_code}")
# #     if res.status_code in [200, 201]:
# #         print("✅ Upload successful.")
# #     else:
# #         print("❌ Upload failed.")
# #         print(res.text)

# def upload_file(content_str, path):
#     print(f"📤 Uploading to: {path}")
#     url = f"{API_URL}/{path}"

#     # Check if file exists to get SHA
#     sha = None
#     check = requests.get(url, headers=HEADERS)
#     if check.status_code == 200:
#         sha = check.json().get("sha")
#         print(f"✅ Existing file SHA: {sha}")
#     elif check.status_code == 404:
#         print("📁 File does not exist. Creating new.")
#     else:
#         print(f"❌ Error checking file: {check.status_code}")
#         print(check.text)
#         return

#     payload = {
#         "message": "Updated formatted CSI output",
#         "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
#     }

#     if sha:
#         payload["sha"] = sha

#     res = requests.put(url, headers=HEADERS, json=payload)
#     print(f"🔁 GitHub Response: {res.status_code}")
#     if res.status_code in [200, 201]:
#         print("✅ Upload successful.")
#     else:
#         print("❌ Upload failed.")
#         print(res.text)


# # ========= Formatter Logic =========

# def format_blocks(text):
#     # Match: timestamp\nAmplitude: ...\nPhase: ...
#     pattern = re.compile(r"^(.*?)\nAmplitude: (.*?)\nPhase: (.*?)(?=\n\S|\Z)", re.DOTALL | re.MULTILINE)
#     matches = pattern.findall(text)

#     blocks = []

#     for i, (timestamp, amp_str, phase_str) in enumerate(matches):
#         amplitudes = [float(a.strip()) for a in amp_str.strip().split(',')]
#         phases = [float(p.strip()) for p in phase_str.strip().split(',')]
#         block = f"{timestamp}\n{amplitudes}\n{phases}\n\n"
#         blocks.append(block)

#     return ''.join(blocks)

# # ========= Main ==========

# if __name__ == "__main__":
#     text, _ = get_file(INPUT_FILE_PATH)
#     if text:
#         formatted = format_blocks(text)
#         upload_file(formatted, OUTPUT_FILE_PATH)
