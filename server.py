import http.server
import json
import requests
import google.generativeai as genai
import io
from PIL import Image
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

PORT = 8000
GEMINI_API_KEY = "AIzaSyAiOM0DFyaJOQHqKEy0RQ96U_Ml9YXUqIM"
GEMINI_MODEL_NAME = "gemini-1.5-flash"
MONSTER_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImJhNTZiZDllMTU5OTBmMDcxNWNmMDIwZjM3YTEyMzU2IiwiY3JlYXRlZF9hdCI6IjIwMjQtMDctMjJUMjE6MDk6NDcuODI2NzgyIn0.ZMwUYBi-DNo6tCTW68G3nfrIqEJz11Iltzs7fiY7Xic"
HF_API_KEY = "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"
IMAGE_PATH = "C:\\Users\\ttddlddd\\pythonProject2\\output_image.jpg"

last_image_update = datetime.min

app = Flask(__name__, static_folder='.')
CORS(app)

# Flask routes
@app.route('/ai-response', methods=['POST'])
def ai_response():
    data = request.json
    input_text = data.get('input')
    response = process_input(input_text)
    return jsonify({"response": response})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')
    success = generate_hf_image(prompt)
    if success:
        global last_image_update
        last_image_update = datetime.now()
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure", "error": "Image generation failed"}), 500

@app.route('/image-status', methods=['GET'])
def image_status():
    global last_image_update
    return jsonify({"last_update": last_image_update.isoformat()})

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

def process_input(input_text):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(input_text)
    return response.text

def generate_hf_image(prompt):
    url = "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        if response.status_code == 200 and response.headers.get('Content-Type') in ['image/png', 'image/jpeg']:
            image = Image.open(io.BytesIO(response.content))
            image.save(IMAGE_PATH)
            return True
        else:
            print(f"Unexpected response status or content type: {response.status_code}, {response.headers.get('Content-Type')}")
    except requests.RequestException as e:
        print(f"Error fetching image from Hugging Face API: {e}")
    except Exception as e:
        print(f"Error processing image: {e}")
    return False

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "index.html"
        elif self.path == "/image-status":
            self.handle_image_status()
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/ai-response":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            input_data = json.loads(post_data)
            user_input = input_data['input']

            ai_response = self.get_gemini_response(user_input)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": ai_response}).encode())

        elif self.path == "/generate-image":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            input_data = json.loads(post_data)
            prompt = input_data['prompt']

            success = self.generate_hf_image(prompt)
            if success:
                global last_image_update
                last_image_update = datetime.now()  # Update the timestamp
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "failure", "error": "Image generation failed"}).encode())

    def handle_image_status(self):
        global last_image_update
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"last_update": last_image_update.isoformat()}).encode())

    def get_gemini_response(self, input_text):
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(input_text)
        return response.text

    def generate_hf_image(self, prompt):
        url = "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": prompt}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            if response.status_code == 200 and response.headers.get('Content-Type') in ['image/png', 'image/jpeg']:
                image = Image.open(io.BytesIO(response.content))
                image.save(IMAGE_PATH)
                return True
            else:
                print(f"Unexpected response status or content type: {response.status_code}, {response.headers.get('Content-Type')}")
        except requests.RequestException as e:
            print(f"Error fetching image from Hugging Face API: {e}")
        except Exception as e:
            print(f"Error processing image: {e}")
        return False

def run_flask():
    app.run(port=PORT, use_reloader=False)

def run_http():
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, MyHandler)
    print(f"Serving on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_flask).start()
    run_http("run")