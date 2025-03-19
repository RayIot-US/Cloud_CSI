from flask import Flask, request, jsonify
import json
import requests
import os
import base64
import traceback

app = Flask(__name__)  # Ensure `app` is defined

# GitHub Credentials
GITHUB_USERNAME = "RayIot-US"
GITHUB_REPO = "Cloud_CSI"
GITHUB_TOKEN = os.getenv("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")  # Set this in your environment
GITHUB_FILE_PATH = "csi_data/data.json"  # Stores data in a subfolder

@app.before_request
def log_request():
    """Log all incoming requests."""
    print(f"🔍 Received {request.method} request to {request.path}")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "success", "message": "Server is running!"}), 200

@app.route("/upload", methods=["POST"])
def upload():
    try:
        print("✅ Received request from ESP32")
        data = request.json
        if not data:
            print("❌ No data received!")
            return jsonify({"status": "error", "message": "No data received"}), 400
        print(f"📡 Received Data: {json.dumps(data, indent=4)}")
        return jsonify({"status": "success", "message": "Data received"}), 200
    except Exception as e:
        print(f"🚨 Exception Occurred: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# ✅ Fix for Gunicorn: Ensure `app` is properly defined
if __name__ != "__main__":
    application = app  # Gunicorn looks for `application`

if __name__ == "__main__":
    print("🚀 Flask Server is Starting...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)


# import requests

# def test_github_access():
#     """Test if Render Cloud can access GitHub API"""
#     print("🔍 Testing GitHub API connectivity...")

#     try:
#         response = requests.get("https://api.github.com")

#         print(f"🔍 GitHub API Test Response: {response.status_code}")

#         if response.status_code == 200:
#             print("✅ GitHub API is reachable!")
#         elif response.status_code == 403:
#             print("❌ GitHub API is blocked! Render Cloud may be restricted.")
#         else:
#             print(f"⚠️ Unexpected Response: {response.text}")

#     except Exception as e:
#         print(f"🚨 Error connecting to GitHub: {str(e)}")

# # Run the test
# if __name__ == "__main__":
#     test_github_access()




# from flask import Flask, request, jsonify
# import json
# import requests
# import os
# import base64
# import traceback

# app = Flask(__name__)

# # GitHub Credentials (Use Environment Variables for Security)
# GITHUB_USERNAME = "RayIot-US"
# GITHUB_REPO = "Cloud_CSI"
# #GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Secure token storage
# GITHUB_TOKEN = os.getenv("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")  # Set this in your environment

# GITHUB_FILE_PATH = "data.json"

# @app.before_request
# def log_request():
#     """Logs all incoming requests."""
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
        
#         if response.status_code == 200:
#             sha = response.json().get("sha", None)
#             print(f"✅ File found, SHA: {sha}")
#         elif response.status_code == 404:
#             sha = None
#             print("⚠️ File does not exist, creating a new one.")
#         else:
#             print(f"❌ Error fetching file info from GitHub: {response.text}")
#             return response.status_code

#         # Convert data to JSON format and Base64 encode it
#         json_data = json.dumps(data, indent=4)
#         json_data_b64 = base64.b64encode(json_data.encode()).decode()

#         # Prepare the payload
#         payload = {
#             "message": "Update CSI data",
#             "content": json_data_b64,  # Use Base64 encoding
#             "sha": sha if sha else None  # Include SHA only if updating
#         }

#         print("📤 Uploading CSI data to GitHub...")
#         response = requests.put(url, headers=headers, json=payload)

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
#     """ Root route to test if the server is running """
#     return jsonify({"status": "success", "message": "Server is running!"}), 200

# @app.route("/upload", methods=["POST"])
# def upload():
#     """ Receive CSI data from ESP32 and upload it to GitHub """
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

# if __name__ == "__main__":
#     print("🚀 Flask Server is Starting...")
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)



# # import os
# # from flask import Flask, request, jsonify

# # app = Flask(__name__)

# # @app.route("/", methods=["GET"])
# # def home():
# #     return jsonify({"status": "success", "message": "Server is running!"}), 200

# # @app.route("/upload", methods=["POST"])
# # def upload():
# #     try:
# #         data = request.json
# #         if not data:
# #             return jsonify({"status": "error", "message": "No data received"}), 400
# #         print(f"📡 Received Data: {data}")
# #         return jsonify({"status": "success", "message": "Data received"}), 200
# #     except Exception as e:
# #         print(f"🚨 Error: {e}")
# #         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # if __name__ == "__main__":
# #     print("🚀 Flask Server is Starting...")
# #     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)




# #working

# # from flask import Flask, request, jsonify

# # app = Flask(__name__)

# # @app.before_request
# # def log_request():
# #     print(f"🔍 Received {request.method} request to {request.path}")

# # @app.route('/', methods=['GET'])
# # def home():
# #     return jsonify({"status": "success", "message": "Server is running!"}), 200

# # @app.route('/upload', methods=['POST'])
# # def upload():
# #     """ Receive CSI data from ESP32 """
# #     try:
# #         data = request.json
# #         if not data:
# #             print("❌ No data received!")
# #             return jsonify({"status": "error", "message": "No data received"}), 400
        
# #         print(f"📡 Received Data: {data}")

# #         # Respond to ESP32
# #         return jsonify({"status": "success", "message": "Data received"}), 200
# #     except Exception as e:
# #         print(f"🚨 Error processing request: {str(e)}")
# #         return jsonify({"status": "error", "message": "Internal Server Error"}), 500

# # if __name__ == '__main__':
# #     app.run(host="0.0.0.0", port=5000)



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
# # GITHUB_TOKEN = os.getenv("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")  # Set this in your environment
# # GITHUB_FILE_PATH = "data.json"
# # # GITHUB_TOKEN = "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"

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
# #         else:
# #             print(f"❌ Failed to save data to GitHub! Response: {response.text}")

# #         return response.status_code
# #     except Exception as e:
# #         print(f"🚨 Exception Occurred: {str(e)}")
# #         traceback.print_exc()
# #         return 500

# # @app.route('/upload', methods=['POST'])
# # def upload():
# #     """ Receive CSI data from ESP32 and upload it to GitHub """
# #     try:
# #         print("✅ Received request from ESP32")
        
# #         data = request.json
# #         if not data:
# #             print("❌ No data received!")
# #             return jsonify({"status": "error", "message": "No data received"}), 400

# #         print(f"📡 Received Data: {data}")

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

# # if __name__ == '__main__':
# #     app.run(host="0.0.0.0", port=5000)




# # from flask import Flask, request, jsonify
# # import json
# # import os
# # import requests
# # app = Flask(__name__)
# # # GitHub Credentials (Replace with your details)
# # GITHUB_USERNAME = "RayIot-US"
# # GITHUB_REPO = "Cloud_CSI"
# # #GITHUB_TOKEN = "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"
# # GITHUB_TOKEN = "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"
# # GITHUB_FILE_PATH = "data.json"
# # def upload_to_github(data):
# #     """ Upload CSI data to GitHub as JSON """
# #     url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
# #     headers = {
# #         "Authorization": f"token {GITHUB_TOKEN}",
# #         "Accept": "application/vnd.github.v3+json"
# #     }
# #     # Get the existing file SHA (needed for updates)
# #     response = requests.get(url, headers=headers)
# #     if response.status_code == 200:
# #         sha = response.json()["sha"]
# #     else:
# #         sha = None
# #     # Convert data to JSON format
# #     json_data = json.dumps(data, indent=4)
# #     # Prepare the payload
# #     payload = {
# #         "message": "Update CSI data",
# #         "content": json_data.encode("utf-8").hex(),  # Encode data to hex
# #         "sha": sha  # Required if updating existing file
# #     }
# #     # Upload to GitHub
# #     response = requests.put(url, headers=headers, json=payload)
# #     return response.status_code
# # @app.route('/upload', methods=['POST'])
# # def upload():
# #     """ Receive CSI data from ESP32 and upload it to GitHub """
# #     data = request.json
# #     if not data:
# #         return jsonify({"status": "error", "message": "No data received"}), 400
# #     # Upload to GitHub
# #     status = upload_to_github(data)
# #     if status == 200 or status == 201:
# #         return jsonify({"status": "success", "message": "CSI data saved to GitHub"}), 200
# #     else:
# #         return jsonify({"status": "error", "message": "Failed to save to GitHub"}), 500
# # if __name__ == '__main__':
# #     app.run(host="0.0.0.0", port=5000)






