import pandas as pd
import requests
import base64
import os
from io import StringIO
from scipy.signal import butter, filtfilt

# === GitHub Setup ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
INPUT_FILE_PATH = "csi_data/structured_2.csv"
OUTPUT_FILE_PATH = "csi_data/filtered_output_1.csv"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# === Filter Params ===
sampling_rate = 20  # Hz
lowcut = 4.0
highcut = 9.0

# === GitHub Functions ===
def download_from_github(filepath):
    url = f"{API_URL}/{filepath}"
    print(f"📥 Downloading: {filepath}")
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        content = base64.b64decode(res.json()["content"]).decode()
        return content
    else:
        print(f"❌ Failed to fetch file. Status: {res.status_code}")
        return None

def upload_to_github(filepath, content_str, commit_msg="Upload filtered output"):
    url = f"{API_URL}/{filepath}"
    print(f"📤 Uploading: {filepath}")

    sha = None
    check = requests.get(url, headers=HEADERS)
    if check.status_code == 200:
        sha = check.json().get("sha")
        print(f"✅ Existing file SHA: {sha}")
    elif check.status_code != 404:
        print(f"❌ Error checking file: {check.status_code}")
        return

    payload = {
        "message": commit_msg,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    }
    if sha:
        payload["sha"] = sha

    res = requests.put(url, headers=HEADERS, json=payload)
    print(f"🔁 GitHub Response: {res.status_code}")
    print(res.text)

# === Signal Processing Functions ===
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    return butter(order, [low, high], btype='band')

def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    return filtfilt(b, a, data, axis=0)

# === Main Logic ===
def main():
    raw_csv = download_from_github(INPUT_FILE_PATH)
    if not raw_csv:
        print("❌ Failed to fetch input.")
        return

    df = pd.read_csv(StringIO(raw_csv))
    #df = pd.read_csv(pd.compat.StringIO(raw_csv))
    amp_data = df.drop(columns=["Timestamp"]).values
    filtered_data = apply_bandpass_filter(amp_data, lowcut, highcut, sampling_rate)

    filtered_df = pd.DataFrame(filtered_data, columns=df.columns[1:])
    filtered_df.insert(0, "Timestamp", df["Timestamp"])
    csv_output = filtered_df.to_csv(index=False)

    upload_to_github(OUTPUT_FILE_PATH, csv_output, "Upload bandpass-filtered CSI")

if __name__ == "__main__":
    main()
