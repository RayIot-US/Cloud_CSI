import requests
import base64
import os
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import datetime

# GitHub Setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ========= GitHub File Handling =========

def download_file_from_github(filepath, local_filename):
    print(f"📥 Downloading {filepath} from GitHub...")
    url = f"{API_URL}/{filepath}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        content = base64.b64decode(res.json()["content"])
        with open(local_filename, 'wb') as f:
            f.write(content)
        print(f"✅ Saved as {local_filename}")
    else:
        print(f"❌ Failed to download {filepath}: {res.status_code}")
        print(res.text)

def upload_file_to_github(local_path, repo_path):
    print(f"📤 Uploading {repo_path} to GitHub...")
    url = f"{API_URL}/{repo_path}"
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # Check if file exists
    check = requests.get(url, headers=HEADERS)
    sha = None
    if check.status_code == 200:
        sha = check.json().get("sha")

    payload = {
        "message": f"Update {repo_path}",
        "content": content
    }
    if sha:
        payload["sha"] = sha

    res = requests.put(url, headers=HEADERS, json=payload)
    print(f"🔁 GitHub Response: {res.status_code}")
    if res.status_code in [200, 201]:
        print("✅ Upload successful.")
    else:
        print("❌ Upload failed.")
        print(res.text)

# ========= Your Processing Functions =========

def load_and_process_data(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    data = []
    i = 0
    while i < len(lines):
        timestamp_line = lines[i].strip()
        amplitude_line = lines[i + 1].strip()
        phase_line = lines[i + 2].strip()

        timestamp = timestamp_line
        amplitudes = eval(amplitude_line)
        phases = eval(phase_line)

        data.append([timestamp] + amplitudes)
        i += 4

    df = pd.DataFrame(data)
    df.to_csv("structured_1.csv", index=False)

def add_microseconds_to_timestamp(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    timestamps = []
    for ts in df.iloc[:, 0]:
        dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        ts_with_ms = dt + datetime.timedelta(milliseconds=np.random.randint(0, 1000))
        timestamps.append(ts_with_ms.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

    df.iloc[:, 0] = timestamps
    df.to_csv(output_csv, index=False)

def resample_to_fixed_rate(df, target_rate):
    df["timestamp"] = pd.to_datetime(df.iloc[:, 0])
    df.set_index("timestamp", inplace=True)
    df = df.sort_index()

    start_time = df.index[0]
    end_time = df.index[-1]
    delta = datetime.timedelta(seconds=1 / target_rate)

    new_index = []
    t = start_time
    while t <= end_time:
        new_index.append(t)
        t += delta

    resampled_df = df.reindex(df.index.union(new_index)).interpolate(method='time').reindex(new_index)
    resampled_df.reset_index(inplace=True)
    return resampled_df

def process_all_amplitudes(df):
    numeric_df = df.iloc[:, 1:].astype(float)
    processed = (numeric_df - numeric_df.mean()) / numeric_df.std()
    processed.insert(0, "timestamp", df.iloc[:, 0])
    return processed

def process_subcarriers_with_mad_and_pca(df, top_k=10, n_components=1):
    numeric_data = df.iloc[:, 1:].astype(float)
    mad_scores = np.median(np.abs(numeric_data - np.median(numeric_data, axis=0)), axis=0)
    top_k_indices = np.argsort(mad_scores)[-top_k:]

    selected_data = numeric_data.iloc[:, top_k_indices]
    pca = PCA(n_components=n_components)
    principal_components = pca.fit_transform(selected_data)

    pca_df = pd.DataFrame(principal_components, columns=[f"PC{i+1}" for i in range(n_components)])
    pca_df.insert(0, "timestamp", df["timestamp"])
    pca_df.to_csv("pca_and_time_filtered_selected.csv", index=False)
    return pca_df

# ========= Main Execution =========

def main():
    # Step 1: Download formatted file from GitHub
    download_file_from_github("csi_data/formatted_output.csv", "formatted_output.csv")

    # Step 2: Process pipeline
    load_and_process_data("formatted_output.csv")
    add_microseconds_to_timestamp("structured_1.csv", "output_with_ms_1.csv")

    df = pd.read_csv("output_with_ms_1.csv")
    resampled_df = resample_to_fixed_rate(df, target_rate=20)
    processed_df = process_all_amplitudes(resampled_df)
    pca_df = process_subcarriers_with_mad_and_pca(processed_df, top_k=10, n_components=1)

    # Step 3: Upload selected output files back to GitHub
    upload_file_to_github("structured_1.csv", "csi_data/structured_1.csv")
    upload_file_to_github("output_with_ms_1.csv", "csi_data/output_with_ms_1.csv")
    upload_file_to_github("pca_and_time_filtered_selected.csv", "csi_data/pca_and_time_filtered_selected.csv")

if __name__ == "__main__":
    main()
