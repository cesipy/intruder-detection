import os
import cv2
import socketio
import time

import socketio.exceptions
from glob import glob

from config import *
from utils import Frame
from logger import Logger

from flask import Flask, render_template, request, jsonify
from iot import Iot
from utils import Frame
import cv2
import numpy as np


logger = Logger()
time.sleep(INITIAL_DELAY)
app = Flask(__name__)
iot = Iot()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>IoT Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .status { margin: 20px 0; }
            #preview { max-width: 100%; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>IoT Camera Demo</h1>
        <input type="file" id="imageInput" accept="image/*">
        <button onclick="sendImage()">Send Image</button>
        <div class="status" id="status"></div>
        <img id="preview">

        <script>
            function sendImage() {
                const input = document.getElementById('imageInput');
                const status = document.getElementById('status');
                
                if (!input.files[0]) {
                    status.textContent = 'Please select an image first';
                    return;
                }

                const formData = new FormData();
                formData.append('image', input.files[0]);

                status.textContent = 'Sending...';
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    status.textContent = data.message;
                })
                .catch(error => {
                    status.textContent = 'Error: ' + error;
                });
            }

            // Preview image
            document.getElementById('imageInput').onchange = function(e) {
                const preview = document.getElementById('preview');
                preview.src = URL.createObjectURL(e.target.files[0]);
            };
        </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'message': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No image selected'}), 400

    try:
        nparr = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
 
        retval, jpg = cv2.imencode('.jpg', img)
        data = jpg.tobytes()
        
        frame_name = f"demo_{int(time.time())}.jpg"
        frame_obj = Frame(frame_name, data)
        success = iot._send_frame(frame_obj)
        
        if success:
            return jsonify({'message': f'Successfully sent image: {frame_name}'})
        else:
            return jsonify({'message': 'Failed to send image'}), 500
            
    except Exception as e:
        return jsonify({'message': f'Error processing image: {str(e)}'}), 500

if __name__ == '__main__':
    iot._safe_connect()
    
    app.run(host='0.0.0.0', port=5010)