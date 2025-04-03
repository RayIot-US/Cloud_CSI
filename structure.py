import pandas as pd
import json
import base64
import os
import requests

# GitHub Setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
INPUT_FILE = "csi_data/formatted_output.csv"
OUTPUT_FILE = "csi_data/structured_2.csv"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def download_from_github(filepath):
    url = f"{API_URL}/{filepath}"
    print(f"📥 Downloading from GitHub: {filepath}")
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        content = base64.b64decode(res.json()["content"]).decode()
        return content
    else:
        print(f"❌ Failed to fetch file: {res.status_code}")
        return None

def upload_to_github(filepath, content_str, commit_msg="Upload structured CSV"):
    url = f"{API_URL}/{filepath}"
    print(f"📤 Uploading to GitHub: {filepath}")

    sha = None
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        sha = res.json().get("sha")
        print(f"✅ Existing SHA: {sha}")
    elif res.status_code != 404:
        print("❌ GitHub check error.")
        return

    payload = {
        "message": commit_msg,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha

    put = requests.put(url, headers=HEADERS, json=payload)
    print(f"🔁 GitHub Response: {put.status_code}")
    print(put.text)

def process_csv(csv_text):
    lines = csv_text.strip().splitlines()
    series_data = pd.Series(lines).str.strip()
    cleaned_series = series_data[series_data != ""]
    
    reshaped_df = pd.DataFrame({
        "Timestamp": cleaned_series.iloc[::3].values,
        "Amplitude": cleaned_series.iloc[1::3].apply(json.loads).values,
    })

    column_names_amp = [f"amp_{i}" for i in range(1, 65)]
    amplitude_df = pd.DataFrame(reshaped_df['Amplitude'].tolist(), columns=column_names_amp)
    reshaped_df = reshaped_df.drop(columns=["Amplitude"])

    data = pd.concat([reshaped_df, amplitude_df], axis=1)
    data["Timestamp"] = pd.to_datetime(data["Timestamp"], format='mixed', dayfirst=True)
    data.set_index('Timestamp', inplace=True)

    csv_output = data.to_csv()
    return csv_output

def main():
    csv_raw = download_from_github(INPUT_FILE)
    if csv_raw:
        structured_csv = process_csv(csv_raw)
        upload_to_github(OUTPUT_FILE, structured_csv, "Upload structured CSV output")

if __name__ == "__main__":
    main()
