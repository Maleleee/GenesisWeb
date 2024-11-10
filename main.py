from website import create_app
from threading import Thread, Lock
import time
import numpy as np
import pandas as pd
import logging
import os
from flask import jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import csv
from website.mlmodel import model, label_encoder, preprocess_data  # Adjusted import
from datetime import datetime, timezone

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Flask app and SocketIO
app = create_app()
socketio = SocketIO(app)
CORS(app, origins=["http://localhost:5000", "http://127.0.0.1:5000"])

# Global variables
last_request_time = None
data_path = os.environ.get('DATA_PATH', "network_traffic_data.csv")
data = pd.read_csv(data_path)

# Prepare label data for attack simulations
label_data = {
    label: data[data['label'] == label][['packet_size', 'request_rate']].values
    for label in data['label'].unique()
}

# Global variable to store attack data
attack_data = []

# Initialize a lock for thread safety
lock = Lock()

def simulate_attack(duration=60):
    """Simulate an attack and emit the data to the dashboard for a specified duration."""
    global attack_data
    csv_file_path = 'attack_data.csv'
    start_time = time.time()
    
    label_counts = {'Normal': 0, 'DDOS': 0, 'Port_Scan': 0, 'SYN_Flood': 0, 'ICMP_Flood': 0}  # Initialize label counts

    while time.time() - start_time < duration:
        try:
            # Generate random attack data
            packet_size = np.random.randint(500, 1500)
            request_rate = np.random.randint(1, 100)
            attack_event = {
                'timestamp': datetime.now(timezone.utc).isoformat(),  # Use timezone-aware timestamp
                'ip': f"192.168.0.{np.random.randint(1, 255)}",  # Random IP
                'packet_size': packet_size,  # Random packet size
                'request_rate': request_rate,  # Random request rate
            }

            # Prepare data for prediction
            input_data = pd.DataFrame({'packet_size': [packet_size], 'request_rate': [request_rate]})
            input_scaled = preprocess_data(input_data)

            # Predict the label using the model
            predictions = model.predict(input_scaled)
            predicted_class = np.argmax(predictions, axis=1)[0]
            label = label_encoder.inverse_transform([predicted_class])[0]

            # Log the predicted label
            logger.debug(f"Predicted label: {label}")

            # Ensure consistent label names
            if label == 'normal':
                label = 'Normal'
            elif label == 'ddos':
                label = 'DDOS'
            elif label == 'port_scan':
                label = 'Port_Scan'
            elif label == 'syn_flood':
                label = 'SYN_Flood'
            elif label == 'icmp_flood':
                label = 'ICMP_Flood'

            # Add the predicted label to the attack event
            attack_event['label'] = label

            # Update label counts in a thread-safe manner
            with lock:
                if label in label_counts:
                    label_counts[label] += 1
                    logger.debug(f"Updated label counts: {label_counts}")
                else:
                    logger.error(f"Unexpected label: {label}")
                    continue

                # Append to attack_data
                attack_data.append(attack_event)

                # Write to CSV
                with open(csv_file_path, mode='a', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=attack_event.keys())
                    if file.tell() == 0:  # Check if the file is empty
                        writer.writeheader()  # Write header if file is empty
                    writer.writerow(attack_event)

                # Emit the new attack event to all connected clients
                socketio.emit('new_attack', attack_event)

                # Optional: Emit the updated attack_data to all clients
                socketio.emit('update_user_data', attack_data)

            logger.info(f"Simulated Attack: {attack_event}")
            logger.info(f"Label Counts: {label_counts}")  # Log label counts
        except Exception as e:
            logger.error(f"Error during attack simulation: {e}")

        time.sleep(1)  # Reduce sleep time to 0.1 seconds for faster processing

@app.before_request
def before_request():
    global last_request_time
    last_request_time = time.time()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@socketio.on('connect')
def on_connect():
    emit('connected', {'message': 'Connected to the server'})
    logger.info("Client connected")

@socketio.on('disconnect')
def on_disconnect():
    logger.info("Client disconnected")

if __name__ == '__main__':
    # Start the attack simulation in a separate thread with a duration of 20 seconds
    model_thread = Thread(target=simulate_attack, args=(20,))
    model_thread.daemon = True  # Exit the thread when the main program exits
    model_thread.start()

    # Run the Flask app
    socketio.run(app, debug=True)