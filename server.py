import base64
import requests
import json
import os
import traceback
from flask import Flask, request, jsonify

app = Flask(__name__)

# GitHub Credentials
GITHUB_USERNAME = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_FILE_PATH = "csi_data/raw_csi_data.txt"

@app.before_request
def log_request():
    print(f"🔍 Received {request.method} request to {request.path}")

# def upload_to_github(new_raw_data):
#     """ Append CSI data to GitHub file instead of replacing it """
#     try:
#         url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#         headers = {
#             "Authorization": f"token {GITHUB_TOKEN}",
#             "Accept": "application/vnd.github.v3+json"
#         }

#         print("🔍 Checking if file exists on GitHub...")
#         response = requests.get(url, headers=headers)
#         sha = None
#         existing_data = ""

#         if response.status_code == 200:
#             sha = response.json()["sha"]
#             print(f"✅ File found, SHA: {sha}")
#             existing_base64 = response.json()["content"]
#             existing_data = base64.b64decode(existing_base64).decode("utf-8")
#         elif response.status_code == 404:
#             print("⚠️ File does not exist. A new file will be created.")
#         else:
#             print(f"❌ Error fetching file: {response.status_code} {response.text}")
#             return response.status_code

#         # Append new data to existing data
#         combined_data = existing_data + "\n" + new_raw_data

#         encoded_data = base64.b64encode(combined_data.encode()).decode()

#         payload = {
#             "message": "Appended new CSI data",
#             "content": encoded_data,
#             "sha": sha if sha else None
#         }

#         print("📤 Uploading updated file to GitHub...")
#         put_response = requests.put(url, headers=headers, json=payload)
#         print(f"🔁 GitHub PUT Response: {put_response.status_code}")
#         print(put_response.text)

#         if put_response.status_code in [200, 201]:
#             print("✅ Data appended to GitHub.")
#             return 200
#         else:
#             print("❌ Failed to update GitHub file.")
#             return put_response.status_code

#     except Exception as e:
#         print(f"🚨 Exception Occurred: {str(e)}")
#         traceback.print_exc()
#         return 500

# def upload_to_github(new_raw_data):
#     """ Append new raw CSI text to GitHub file instead of replacing it """
#     try:
#         url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#         headers = {
#             "Authorization": f"token {GITHUB_TOKEN}",
#             "Accept": "application/vnd.github.v3+json"
#         }

#         print("🔍 Checking if file exists on GitHub...")
#         response = requests.get(url, headers=headers)
#         sha = None
#         existing_data = ""

#         if response.status_code == 200:
#             sha = response.json()["sha"]
#             print(f"✅ File found, SHA: {sha}")
#             base64_content = response.json()["content"]
#             existing_data = base64.b64decode(base64_content).decode("utf-8")
#         elif response.status_code == 404:
#             print("⚠️ File not found, will create new one.")
#         else:
#             print(f"❌ Error reading from GitHub: {response.status_code}")
#             return response.status_code

#         # Append new data to existing content
#         combined_data = existing_data.strip() + "\n\n" + new_raw_data.strip()

#         # Encode the full text
#         encoded = base64.b64encode(combined_data.encode("utf-8")).decode("utf-8")

#         payload = {
#             "message": "Append CSI data",
#             "content": encoded,
#             "sha": sha if sha else None
#         }

#         print("📤 Uploading updated file...")
#         put_response = requests.put(url, headers=headers, json=payload)
#         print(f"🔁 GitHub Response: {put_response.status_code}")
#         print(put_response.text)

#         if put_response.status_code in [200, 201]:
#             print("✅ Raw CSI appended to GitHub successfully.")
#             return 200
#         else:
#             print("❌ GitHub PUT failed.")
#             return put_response.status_code

#     except Exception as e:
#         print(f"🚨 Exception occurred: {str(e)}")
#         traceback.print_exc()
#         return 500

def upload_to_github(new_json_data):
    """ Parse CSI JSON, format it as line-by-line raw text, and append to GitHub file """
    try:
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Get existing content
        response = requests.get(url, headers=headers)
        sha = None
        existing_data = ""

        if response.status_code == 200:
           # sha = response.json()["sha"]
            sha = response.json().get("sha", None)
            print(f"🔍 SHA fetched from GitHub: {sha}")

            existing_base64 = response.json()["content"]
            existing_data = base64.b64decode(existing_base64).decode("utf-8")
            print(f"✅ Existing file found. Appending...")
        elif response.status_code == 404:
            print("📁 No file found. A new one will be created.")
        else:
            print(f"❌ Error fetching file: {response.status_code}")
            return response.status_code

        # Parse incoming JSON string into Python dict
        parsed = json.loads(new_json_data)
        csi_entries = parsed.get("csi_data", [])

        # Format each entry as "Timestamp + CSI Data"
        new_text = ""
        for entry in csi_entries:
            timestamp = entry.get("timestamp", "unknown")
            values = entry.get("csi_values", [])
            values_str = " ".join(map(str, values))
            #new_text += f"Timestamp: {timestamp}\nCSI Data: {values_str}\n\n"
            new_text += f"{timestamp}\nCSI Data: {values_str}\n\n"

        # Append to existing data
        combined_data = existing_data.strip() + "\n" + new_text.strip()
        encoded_content = base64.b64encode(combined_data.encode()).decode()

        # Push back to GitHub
        payload = {
            "message": "Append formatted CSI data",
            "content": encoded_content,
            "sha": sha if sha else None
        }

        put_response = requests.put(url, headers=headers, json=payload)
        print(f"🔁 GitHub Response: {put_response.status_code}")
        print(put_response.text)

        return put_response.status_code

    except Exception as e:
        print(f"🚨 Exception occurred: {str(e)}")
        traceback.print_exc()
        return 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "success", "message": "Server is running!"}), 200

#uncomment this working
# @app.route("/upload", methods=["POST"])
# def upload():
#     try:
#         print("✅ Received request from ESP32")
#         raw_data = request.data.decode("utf-8")
#         if not raw_data:
#             print("❌ No data received!")
#             return jsonify({"status": "error", "message": "No data received"}), 400
#         print(f"📡 Received RAW Data:\n{raw_data}")

#         status = upload_to_github(raw_data)

#         if status in [200, 201]:
#             return jsonify({"status": "success", "message": "RAW CSI data appended to GitHub"}), 200
#         else:
#             return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
#     except Exception as e:
#         print(f"🚨 Exception Occurred: {str(e)}")
#         traceback.print_exc()
#         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@app.route("/upload", methods=["POST"])
def upload():
    try:
        print("✅ Received request from ESP32")
        raw_data = request.data.decode("utf-8")
        if not raw_data:
            print("❌ No data received!")
            return jsonify({"status": "error", "message": "No data received"}), 400
        print(f"📡 Received RAW Data:\n{raw_data}")

        status = upload_to_github(raw_data)

        if status in [200, 201]:
            try:
                import subprocess
                subprocess.run(["python3", "process_csi_cloud.py"], check=True)
                print("✅ Ran processor.py after upload.")
            except Exception as e:
                print("❌ Failed to run processor.py")
                print(e)
                print("STDERR:", e.stderr)

        


            return jsonify({"status": "success", "message": "RAW CSI data appended to GitHub"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
    except Exception as e:
        print(f"🚨 Exception Occurred: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


# Gunicorn compatibility
if __name__ != "__main__":
    application = app

if __name__ == "__main__":
    print("🚀 Flask Server is Starting...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)

#new to run process.py automatically
# import subprocess

# # After successful upload
# if status in [200, 201]:
#     try:
#         subprocess.run(["python", "process_csi_cloud.py"], check=True)
#         print("✅ processor.py executed after upload.")
#     except Exception as e:
#         print("❌ Failed to run processor.py")
#         print(e)


#working latest
# import base64  # 🔴 Add this line
# import requests
# import json
# import os
# import traceback
# from flask import Flask, request, jsonify

# app = Flask(__name__)  # Ensure `app` is defined

# # from flask import Flask, request, jsonify
# # import requests
# # import os
# # import traceback

# # app = Flask(__name__)  # Ensure `app` is defined

# # GitHub Credentials
# GITHUB_USERNAME = "RayIot-US"
# GITHUB_REPO = "Cloud_CSI"
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Securely load from Render Cloud environment variable
# GITHUB_FILE_PATH = "csi_data/raw_csi_data.txt"  # Save as raw text

# @app.before_request
# def log_request():
#     """Log all incoming requests."""
#     print(f"🔍 Received {request.method} request to {request.path}")

# def upload_to_github(raw_data):
#     """ Upload CSI data to GitHub as RAW text """
#     try:
#         url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#         headers = {
#             "Authorization": f"token {GITHUB_TOKEN}",
#             "Accept": "application/vnd.github.v3+json"
#         }

#         print("🔍 Checking if file exists on GitHub...")

#         # Get the existing file SHA (needed for updates)
#         response = requests.get(url, headers=headers)
#         sha = None  

#         if response.status_code == 200:
#             sha = response.json().get("sha", None)
#             print(f"✅ File found, SHA: {sha}")
#         elif response.status_code == 404:
#             print("⚠️ File does not exist, creating a new one.")
#         else:
#             print(f"❌ Error fetching file info from GitHub: {response.text}")
#             return response.status_code

#         # Convert data to Base64 (GitHub requires it for text files)
#         raw_data_b64 = base64.b64encode(raw_data.encode()).decode()

#         # Prepare the payload
#         payload = {
#             "message": "Updated RAW CSI data",
#             "content": raw_data_b64,  
#             "sha": sha if sha else None  
#         }

#         print("📤 Uploading RAW CSI data to GitHub...")
#         response = requests.put(url, headers=headers, json=payload)

#         print(f"🔍 GitHub API Response: {response.status_code} {response.text}")

#         if response.status_code in [200, 201]:
#             print("✅ Successfully saved RAW CSI data to GitHub!")
#             return response.status_code
#         else:
#             print(f"❌ Failed to save data to GitHub! Response: {response.text}")
#             return response.status_code

#     except Exception as e:
#         print(f"🚨 Exception Occurred: {str(e)}")
#         traceback.print_exc()
#         return 500

# @app.route("/", methods=["GET"])
# def home():
#     return jsonify({"status": "success", "message": "Server is running!"}), 200

# @app.route("/upload", methods=["POST"])
# def upload():
#     try:
#         print("✅ Received request from ESP32")
#         raw_data = request.data.decode("utf-8")  # Read raw text
#         if not raw_data:
#             print("❌ No data received!")
#             return jsonify({"status": "error", "message": "No data received"}), 400
#         print(f"📡 Received RAW Data:\n{raw_data}")

#         # Upload raw data to GitHub
#         status = upload_to_github(raw_data)

#         if status in [200, 201]:
#             return jsonify({"status": "success", "message": "RAW CSI data saved to GitHub"}), 200
#         else:
#             return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
#     except Exception as e:
#         print(f"🚨 Exception Occurred: {str(e)}")
#         traceback.print_exc()
#         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # ✅ Fix for Gunicorn: Ensure `app` is properly defined
# if __name__ != "__main__":
#     application = app  # Gunicorn looks for `application`

# if __name__ == "__main__":
#     print("🚀 Flask Server is Starting...")
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)



#working
# from flask import Flask, request, jsonify
# import json
# import requests
# import os
# import base64
# import traceback

# app = Flask(__name__)  # Ensure `app` is defined

# # GitHub Credentials
# GITHUB_USERNAME = "RayIot-US"
# GITHUB_REPO = "Cloud_CSI"
#   # Securely load from Render Cloud environment variable
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# GITHUB_FILE_PATH = "csi_data/data.json"  # Stores data in a subfolder

# @app.before_request
# def log_request():
#     """Log all incoming requests."""
#     print(f"🔍 Received {request.method} request to {request.path}")

# def upload_to_github(data):
#     """ Upload CSI data to GitHub as JSON """
#     try:
#         url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#         headers = {
#             "Authorization": f"token {GITHUB_TOKEN}",
#             "Accept": "application/vnd.github.v3+json"
#         }

#         print("🔍 Checking if file exists on GitHub...")

#         # Get the existing file SHA (needed for updates)
#         response = requests.get(url, headers=headers)
#         sha = None  # Default to None (used when creating a new file)

#         if response.status_code == 200:
#             sha = response.json().get("sha", None)
#             print(f"✅ File found, SHA: {sha}")
#         elif response.status_code == 404:
#             print("⚠️ File does not exist, creating a new one.")
#         else:
#             print(f"❌ Error fetching file info from GitHub: {response.text}")
#             return response.status_code

#         # Convert data to JSON format and Base64 encode it
#         json_data = json.dumps(data, indent=4)
#         json_data_b64 = base64.b64encode(json_data.encode()).decode()

#         # Prepare the payload
#         payload = {
#             "message": "Updated CSI data",
#             "content": json_data_b64,  # Use Base64 encoding
#             "sha": sha if sha else None  # Include SHA to update existing file
#         }

#         print("📤 Uploading CSI data to GitHub...")
#         response = requests.put(url, headers=headers, json=payload)

#         # 🔴 Print the exact error message from GitHub API
#         print(f"🔍 GitHub API Response: {response.status_code} {response.text}")

#         if response.status_code in [200, 201]:
#             print("✅ Successfully saved CSI data to GitHub!")
#             return response.status_code
#         else:
#             print(f"❌ Failed to save data to GitHub! Response: {response.text}")
#             return response.status_code

#     except Exception as e:
#         print(f"🚨 Exception Occurred: {str(e)}")
#         traceback.print_exc()
#         return 500

# @app.route("/", methods=["GET"])
# def home():
#     return jsonify({"status": "success", "message": "Server is running!"}), 200

# @app.route("/upload", methods=["POST"])
# def upload():
#     try:
#         print("✅ Received request from ESP32")
#         data = request.json
#         if not data:
#             print("❌ No data received!")
#             return jsonify({"status": "error", "message": "No data received"}), 400
#         print(f"📡 Received Data: {json.dumps(data, indent=4)}")

#         # Upload data to GitHub
#         status = upload_to_github(data)

#         if status in [200, 201]:
#             return jsonify({"status": "success", "message": "CSI data saved to GitHub"}), 200
#         else:
#             return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
#     except Exception as e:
#         print(f"🚨 Exception Occurred: {str(e)}")
#         traceback.print_exc()
#         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # ✅ Fix for Gunicorn: Ensure `app` is properly defined
# if __name__ != "__main__":
#     application = app  # Gunicorn looks for `application`

# if __name__ == "__main__":
#     print("🚀 Flask Server is Starting...")
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)



# import os
# import requests

# def test_github_access():
#     """Test if Render Cloud can access GitHub API with the token"""
#     print("🔍 Testing GitHub API connectivity...")

#     headers = {
#         "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
#         "Accept": "application/vnd.github.v3+json"
#     }

#     response = requests.get("https://api.github.com/user", headers=headers)

#     print(f"🔍 GitHub API Test Response: {response.status_code} {response.text}")

# test_github_access()

# from flask import Flask, request, jsonify
# import json
# import requests
# import os
# import base64
# import traceback

# app = Flask(__name__)  # Ensure `app` is defined

# # GitHub Credentials
# GITHUB_USERNAME = "RayIot-US"
# GITHUB_REPO = "Cloud_CSI"
# GITHUB_TOKEN = os.getenv("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")  # Securely load from environment variable
# # GITHUB_TOKEN = os.getenv("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")  # Securely load from environment variable

# GITHUB_FILE_PATH = "csi_data/data.json"  # Stores data in a subfolder

# @app.before_request
# def log_request():
#     """Log all incoming requests."""
#     print(f"🔍 Received {request.method} request to {request.path}")

# def upload_to_github(data):
#     """ Upload CSI data to GitHub as JSON """
#     try:
#         url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#         headers = {
#             "Authorization": f"token {GITHUB_TOKEN}",
#             "Accept": "application/vnd.github.v3+json"
#         }

#         print("🔍 Checking if file exists on GitHub...")

#         # Get the existing file SHA (needed for updates)
#         response = requests.get(url, headers=headers)
#         sha = None  # Default to None (used when creating a new file)

#         if response.status_code == 200:
#             sha = response.json().get("sha", None)
#             print(f"✅ File found, SHA: {sha}")
#         elif response.status_code == 404:
#             print("⚠️ File does not exist, creating a new one.")
#         else:
#             print(f"❌ Error fetching file info from GitHub: {response.text}")
#             return response.status_code

#         # Convert data to JSON format and Base64 encode it
#         json_data = json.dumps(data, indent=4)
#         json_data_b64 = base64.b64encode(json_data.encode()).decode()

#         # Prepare the payload
#         payload = {
#             "message": "Updated CSI data",
#             "content": json_data_b64,  # Use Base64 encoding
#             "sha": sha  # Include SHA to update existing file
#         }

#         print("📤 Uploading CSI data to GitHub...")
#         response = requests.put(url, headers=headers, json=payload)

#         # 🔴 Print the exact error message from GitHub API
#         print(f"🔍 GitHub API Response: {response.status_code} {response.text}")

#         if response.status_code in [200, 201]:
#             print("✅ Successfully saved CSI data to GitHub!")
#             return response.status_code
#         else:
#             print(f"❌ Failed to save data to GitHub! Response: {response.text}")
#             return response.status_code

#     except Exception as e:
#         print(f"🚨 Exception Occurred: {str(e)}")
#         traceback.print_exc()
#         return 500

# @app.route("/", methods=["GET"])
# def home():
#     return jsonify({"status": "success", "message": "Server is running!"}), 200

# @app.route("/upload", methods=["POST"])
# def upload():
#     try:
#         print("✅ Received request from ESP32")
#         data = request.json
#         if not data:
#             print("❌ No data received!")
#             return jsonify({"status": "error", "message": "No data received"}), 400
#         print(f"📡 Received Data: {json.dumps(data, indent=4)}")

#         # Upload data to GitHub
#         status = upload_to_github(data)

#         if status in [200, 201]:
#             return jsonify({"status": "success", "message": "CSI data saved to GitHub"}), 200
#         else:
#             return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
#     except Exception as e:
#         print(f"🚨 Exception Occurred: {str(e)}")
#         traceback.print_exc()
#         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # ✅ Fix for Gunicorn: Ensure `app` is properly defined
# if __name__ != "__main__":
#     application = app  # Gunicorn looks for `application`

# if __name__ == "__main__":
#     print("🚀 Flask Server is Starting...")
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)


# # import requests

# # def test_github_access():
# #     """Test if Render Cloud can access GitHub API with the token"""
# #     print("🔍 Testing GitHub API connectivity...")

# #     headers = {
# #         "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
# #         "Accept": "application/vnd.github.v3+json"
# #     }

# #     response = requests.get("https://api.github.com/user", headers=headers)

# #     print(f"🔍 GitHub API Test Response: {response.status_code} {response.text}")

# # test_github_access()


# # from flask import Flask, request, jsonify
# # import json
# # import requests
# # import os
# # import base64
# # import traceback

# # app = Flask(__name__)  # Ensure `app` is defined

# # # GitHub Credentials
# # GITHUB_USERNAME = "RayIot-US"
# # GITHUB_REPO = "Cloud_CSI"
# # GITHUB_TOKEN = os.getenv("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")  # Securely load from environment variable
# # GITHUB_FILE_PATH = "csi_data/data.json"  # Stores data in a subfolder

# # @app.before_request
# # def log_request():
# #     """Log all incoming requests."""
# #     print(f"🔍 Received {request.method} request to {request.path}")

# # def upload_to_github(data):
# #     """ Upload CSI data to GitHub as JSON """
# #     try:
# #         url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
# #         headers = {
# #             "Authorization": f"token {GITHUB_TOKEN}",
# #             "Accept": "application/vnd.github.v3+json"
# #         }

# #         print("🔍 Checking if file exists on GitHub...")

# #         # Get the existing file SHA (needed for updates)
# #         response = requests.get(url, headers=headers)
# #         sha = None  # Default to None (used when creating a new file)

# #         if response.status_code == 200:
# #             sha = response.json().get("sha", None)
# #             print(f"✅ File found, SHA: {sha}")
# #         elif response.status_code == 404:
# #             print("⚠️ File does not exist, creating a new one.")
# #         else:
# #             print(f"❌ Error fetching file info from GitHub: {response.text}")
# #             return response.status_code

# #         # Convert data to JSON format and Base64 encode it
# #         json_data = json.dumps(data, indent=4)
# #         json_data_b64 = base64.b64encode(json_data.encode()).decode()

# #         # Prepare the payload
# #         payload = {
# #             "message": "Updated CSI data",
# #             "content": json_data_b64,  # Use Base64 encoding
# #             "sha": sha  # Include SHA to update existing file
# #         }

# #         print("📤 Uploading CSI data to GitHub...")
# #         response = requests.put(url, headers=headers, json=payload)

# #         if response.status_code in [200, 201]:
# #             print("✅ Successfully saved CSI data to GitHub!")
# #             return response.status_code
# #         else:
# #             print(f"❌ Failed to save data to GitHub! Response: {response.text}")
# #             return response.status_code

# #     except Exception as e:
# #         print(f"🚨 Exception Occurred: {str(e)}")
# #         traceback.print_exc()
# #         return 500

# # @app.route("/", methods=["GET"])
# # def home():
# #     return jsonify({"status": "success", "message": "Server is running!"}), 200

# # @app.route("/upload", methods=["POST"])
# # def upload():
# #     try:
# #         print("✅ Received request from ESP32")
# #         data = request.json
# #         if not data:
# #             print("❌ No data received!")
# #             return jsonify({"status": "error", "message": "No data received"}), 400
# #         print(f"📡 Received Data: {json.dumps(data, indent=4)}")

# #         # Upload data to GitHub
# #         status = upload_to_github(data)

# #         if status in [200, 201]:
# #             return jsonify({"status": "success", "message": "CSI data saved to GitHub"}), 200
# #         else:
# #             return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
# #     except Exception as e:
# #         print(f"🚨 Exception Occurred: {str(e)}")
# #         traceback.print_exc()
# #         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # # ✅ Fix for Gunicorn: Ensure `app` is properly defined
# # if __name__ != "__main__":
# #     application = app  # Gunicorn looks for `application`

# # if __name__ == "__main__":
# #     print("🚀 Flask Server is Starting...")
# #     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)


# # from flask import Flask, request, jsonify
# # import json
# # import requests
# # import os
# # import base64
# # import traceback

# # app = Flask(__name__)  # Ensure `app` is defined

# # # GitHub Credentials
# # GITHUB_USERNAME = "RayIot-US"
# # GITHUB_REPO = "Cloud_CSI"
# # GITHUB_TOKEN = os.getenv("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")  # Set this in your environment
# # GITHUB_FILE_PATH = "csi_data/data.json"  # Stores data in a subfolder

# # @app.before_request
# # def log_request():
# #     """Log all incoming requests."""
# #     print(f"🔍 Received {request.method} request to {request.path}")

# # @app.route("/", methods=["GET"])
# # def home():
# #     return jsonify({"status": "success", "message": "Server is running!"}), 200

# # @app.route("/upload", methods=["POST"])
# # def upload():
# #     try:
# #         print("✅ Received request from ESP32")
# #         data = request.json
# #         if not data:
# #             print("❌ No data received!")
# #             return jsonify({"status": "error", "message": "No data received"}), 400
# #         print(f"📡 Received Data: {json.dumps(data, indent=4)}")
# #         return jsonify({"status": "success", "message": "Data received"}), 200
# #     except Exception as e:
# #         print(f"🚨 Exception Occurred: {str(e)}")
# #         traceback.print_exc()
# #         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # # ✅ Fix for Gunicorn: Ensure `app` is properly defined
# # if __name__ != "__main__":
# #     application = app  # Gunicorn looks for `application`

# # if __name__ == "__main__":
# #     print("🚀 Flask Server is Starting...")
# #     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)


# # import requests

# # def test_github_access():
# #     """Test if Render Cloud can access GitHub API"""
# #     print("🔍 Testing GitHub API connectivity...")

# #     try:
# #         response = requests.get("https://api.github.com")

# #         print(f"🔍 GitHub API Test Response: {response.status_code}")

# #         if response.status_code == 200:
# #             print("✅ GitHub API is reachable!")
# #         elif response.status_code == 403:
# #             print("❌ GitHub API is blocked! Render Cloud may be restricted.")
# #         else:
# #             print(f"⚠️ Unexpected Response: {response.text}")

# #     except Exception as e:
# #         print(f"🚨 Error connecting to GitHub: {str(e)}")

# # # Run the test
# # if __name__ == "__main__":
# #     test_github_access()




# # from flask import Flask, request, jsonify
# # import json
# # import requests
# # import os
# # import base64
# # import traceback

# # app = Flask(__name__)

# # # GitHub Credentials (Use Environment Variables for Security)
# # GITHUB_USERNAME = "RayIot-US"
# # GITHUB_REPO = "Cloud_CSI"
# # #GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Secure token storage
# # GITHUB_TOKEN = os.getenv("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")  # Set this in your environment

# # GITHUB_FILE_PATH = "data.json"

# # @app.before_request
# # def log_request():
# #     """Logs all incoming requests."""
# #     print(f"🔍 Received {request.method} request to {request.path}")

# # def upload_to_github(data):
# #     """ Upload CSI data to GitHub as JSON """
# #     try:
# #         url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
# #         headers = {
# #             "Authorization": f"token {GITHUB_TOKEN}",
# #             "Accept": "application/vnd.github.v3+json"
# #         }

# #         print("🔍 Checking if file exists on GitHub...")
        
# #         # Get the existing file SHA (needed for updates)
# #         response = requests.get(url, headers=headers)
        
# #         if response.status_code == 200:
# #             sha = response.json().get("sha", None)
# #             print(f"✅ File found, SHA: {sha}")
# #         elif response.status_code == 404:
# #             sha = None
# #             print("⚠️ File does not exist, creating a new one.")
# #         else:
# #             print(f"❌ Error fetching file info from GitHub: {response.text}")
# #             return response.status_code

# #         # Convert data to JSON format and Base64 encode it
# #         json_data = json.dumps(data, indent=4)
# #         json_data_b64 = base64.b64encode(json_data.encode()).decode()

# #         # Prepare the payload
# #         payload = {
# #             "message": "Update CSI data",
# #             "content": json_data_b64,  # Use Base64 encoding
# #             "sha": sha if sha else None  # Include SHA only if updating
# #         }

# #         print("📤 Uploading CSI data to GitHub...")
# #         response = requests.put(url, headers=headers, json=payload)

# #         if response.status_code in [200, 201]:
# #             print("✅ Successfully saved CSI data to GitHub!")
# #             return response.status_code
# #         else:
# #             print(f"❌ Failed to save data to GitHub! Response: {response.text}")
# #             return response.status_code
# #     except Exception as e:
# #         print(f"🚨 Exception Occurred: {str(e)}")
# #         traceback.print_exc()
# #         return 500

# # @app.route("/", methods=["GET"])
# # def home():
# #     """ Root route to test if the server is running """
# #     return jsonify({"status": "success", "message": "Server is running!"}), 200

# # @app.route("/upload", methods=["POST"])
# # def upload():
# #     """ Receive CSI data from ESP32 and upload it to GitHub """
# #     try:
# #         print("✅ Received request from ESP32")
        
# #         data = request.json
# #         if not data:
# #             print("❌ No data received!")
# #             return jsonify({"status": "error", "message": "No data received"}), 400

# #         print(f"📡 Received Data: {json.dumps(data, indent=4)}")

# #         # Upload data to GitHub
# #         status = upload_to_github(data)
        
# #         if status in [200, 201]:
# #             return jsonify({"status": "success", "message": "CSI data saved to GitHub"}), 200
# #         else:
# #             return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
# #     except Exception as e:
# #         print(f"🚨 Exception Occurred: {str(e)}")
# #         traceback.print_exc()
# #         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # if __name__ == "__main__":
# #     print("🚀 Flask Server is Starting...")
# #     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)



# # # import os
# # # from flask import Flask, request, jsonify

# # # app = Flask(__name__)

# # # @app.route("/", methods=["GET"])
# # # def home():
# # #     return jsonify({"status": "success", "message": "Server is running!"}), 200

# # # @app.route("/upload", methods=["POST"])
# # # def upload():
# # #     try:
# # #         data = request.json
# # #         if not data:
# # #             return jsonify({"status": "error", "message": "No data received"}), 400
# # #         print(f"📡 Received Data: {data}")
# # #         return jsonify({"status": "success", "message": "Data received"}), 200
# # #     except Exception as e:
# # #         print(f"🚨 Error: {e}")
# # #         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # # if __name__ == "__main__":
# # #     print("🚀 Flask Server is Starting...")
# # #     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)




# # #working

# # # from flask import Flask, request, jsonify

# # # app = Flask(__name__)

# # # @app.before_request
# # # def log_request():
# # #     print(f"🔍 Received {request.method} request to {request.path}")

# # # @app.route('/', methods=['GET'])
# # # def home():
# # #     return jsonify({"status": "success", "message": "Server is running!"}), 200

# # # @app.route('/upload', methods=['POST'])
# # # def upload():
# # #     """ Receive CSI data from ESP32 """
# # #     try:
# # #         data = request.json
# # #         if not data:
# # #             print("❌ No data received!")
# # #             return jsonify({"status": "error", "message": "No data received"}), 400
        
# # #         print(f"📡 Received Data: {data}")

# # #         # Respond to ESP32
# # #         return jsonify({"status": "success", "message": "Data received"}), 200
# # #     except Exception as e:
# # #         print(f"🚨 Error processing request: {str(e)}")
# # #         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # # if __name__ == '__main__':
# # #     app.run(host="0.0.0.0", port=5000)



# # # from flask import Flask, request, jsonify
# # # import json
# # # import requests
# # # import os
# # # import base64
# # # import traceback

# # # app = Flask(__name__)

# # # # GitHub Credentials (Use Environment Variables for Security)
# # # GITHUB_USERNAME = "RayIot-US"
# # # GITHUB_REPO = "Cloud_CSI"
# # # GITHUB_TOKEN = os.getenv("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")  # Set this in your environment
# # # GITHUB_FILE_PATH = "data.json"
# # # # GITHUB_TOKEN = "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"

# # # def upload_to_github(data):
# # #     """ Upload CSI data to GitHub as JSON """
# # #     try:
# # #         url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
# # #         headers = {
# # #             "Authorization": f"token {GITHUB_TOKEN}",
# # #             "Accept": "application/vnd.github.v3+json"
# # #         }

# # #         print("🔍 Checking if file exists on GitHub...")
        
# # #         # Get the existing file SHA (needed for updates)
# # #         response = requests.get(url, headers=headers)
        
# # #         if response.status_code == 200:
# # #             sha = response.json().get("sha", None)
# # #             print(f"✅ File found, SHA: {sha}")
# # #         elif response.status_code == 404:
# # #             sha = None
# # #             print("⚠️ File does not exist, creating a new one.")
# # #         else:
# # #             print(f"❌ Error fetching file info from GitHub: {response.text}")
# # #             return response.status_code

# # #         # Convert data to JSON format and Base64 encode it
# # #         json_data = json.dumps(data, indent=4)
# # #         json_data_b64 = base64.b64encode(json_data.encode()).decode()

# # #         # Prepare the payload
# # #         payload = {
# # #             "message": "Update CSI data",
# # #             "content": json_data_b64,  # Use Base64 encoding
# # #             "sha": sha if sha else None  # Include SHA only if updating
# # #         }

# # #         print("📤 Uploading CSI data to GitHub...")
# # #         response = requests.put(url, headers=headers, json=payload)

# # #         if response.status_code in [200, 201]:
# # #             print("✅ Successfully saved CSI data to GitHub!")
# # #         else:
# # #             print(f"❌ Failed to save data to GitHub! Response: {response.text}")

# # #         return response.status_code
# # #     except Exception as e:
# # #         print(f"🚨 Exception Occurred: {str(e)}")
# # #         traceback.print_exc()
# # #         return 500

# # # @app.route('/upload', methods=['POST'])
# # # def upload():
# # #     """ Receive CSI data from ESP32 and upload it to GitHub """
# # #     try:
# # #         print("✅ Received request from ESP32")
        
# # #         data = request.json
# # #         if not data:
# # #             print("❌ No data received!")
# # #             return jsonify({"status": "error", "message": "No data received"}), 400

# # #         print(f"📡 Received Data: {data}")

# # #         # Upload data to GitHub
# # #         status = upload_to_github(data)
        
# # #         if status in [200, 201]:
# # #             return jsonify({"status": "success", "message": "CSI data saved to GitHub"}), 200
# # #         else:
# # #             return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
# # #     except Exception as e:
# # #         print(f"🚨 Exception Occurred: {str(e)}")
# # #         traceback.print_exc()
# # #         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # # if __name__ == '__main__':
# # #     app.run(host="0.0.0.0", port=5000)




# # # from flask import Flask, request, jsonify
# # # import json
# # # import os
# # # import requests
# # # app = Flask(__name__)
# # # # GitHub Credentials (Replace with your details)
# # # GITHUB_USERNAME = "RayIot-US"
# # # GITHUB_REPO = "Cloud_CSI"
# # # #GITHUB_TOKEN = "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"
# # # GITHUB_TOKEN = "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"
# # # GITHUB_FILE_PATH = "data.json"
# # # def upload_to_github(data):
# # #     """ Upload CSI data to GitHub as JSON """
# # #     url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
# # #     headers = {
# # #         "Authorization": f"token {GITHUB_TOKEN}",
# # #         "Accept": "application/vnd.github.v3+json"
# # #     }
# # #     # Get the existing file SHA (needed for updates)
# # #     response = requests.get(url, headers=headers)
# # #     if response.status_code == 200:
# # #         sha = response.json()["sha"]
# # #     else:
# # #         sha = None
# # #     # Convert data to JSON format
# # #     json_data = json.dumps(data, indent=4)
# # #     # Prepare the payload
# # #     payload = {
# # #         "message": "Update CSI data",
# # #         "content": json_data.encode("utf-8").hex(),  # Encode data to hex
# # #         "sha": sha  # Required if updating existing file
# # #     }
# # #     # Upload to GitHub
# # #     response = requests.put(url, headers=headers, json=payload)
# # #     return response.status_code
# # # @app.route('/upload', methods=['POST'])
# # # def upload():
# # #     """ Receive CSI data from ESP32 and upload it to GitHub """
# # #     data = request.json
# # #     if not data:
# # #         return jsonify({"status": "error", "message": "No data received"}), 400
# # #     # Upload to GitHub
# # #     status = upload_to_github(data)
# # #     if status == 200 or status == 201:
# # #         return jsonify({"status": "success", "message": "CSI data saved to GitHub"}), 200
# # #     else:
# # #         return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
# # # if __name__ == '__main__':
# # #     app.run(host="0.0.0.0", port=5000)






