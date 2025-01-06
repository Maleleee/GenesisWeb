from website import create_app
from threading import Thread
import time
import numpy as np
import pandas as pd
import logging
import os
from flask import jsonify, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import csv


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

def simulate_attack(): # Change to actual script attack when it's ready, temporarily we have this function to see if the dashboard updates real-time.
    """Simulate an attack and emit the data to the dashboard."""
    global attack_data
    csv_file_path = 'attack_data.csv'

    while True:
        # Generate random attack data
        attack_event = {
            'timestamp': time.time(),  # Add a timestamp
            'ip': f"192.168.0.{np.random.randint(1, 255)}",  # Random IP
            'packet_size': np.random.randint(500, 1500),  # Random packet size
            'request_rate': np.random.randint(1, 100),  # Random request rate
            'label': np.random.choice(['Normal', 'DDOS', 'Port_Scan'])  # Random label  #TODO: use model / dataset as basis for the labels
        }

        # Append to attack_data
        attack_data.append(attack_event)

        # Write to CSV
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=attack_event.keys())
            if file.tell() == 0:  # Check if the file is empty
                writer.writeheader()  # Write header if file is empty
            writer.writerow(attack_event)

        logger.info(f"Simulated Attack: {attack_event}")
        time.sleep(10)  # Wait for 10 seconds before simulating the next attack

        


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
    # Start the attack simulation in a separate thread
    model_thread = Thread(target=simulate_attack)
    model_thread.daemon = True  # Exit the thread when the main program exits
    model_thread.start()

    # Run the Flask app
    socketio.run(app, debug=True)
