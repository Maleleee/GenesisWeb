from website import create_app
from threading import Thread
import time
import numpy as np
import requests  
import pandas as pd

app = create_app()

last_request_time = None

data_path = "C:/Users/User/Documents/GitHub/GenesisWeb/network_traffic_data.csv"
data = pd.read_csv(data_path)

label_data = {
    label: data[data['label'] == label][['packet_size', 'request_rate']].values
    for label in data['label'].unique()
}

def call_model_api(user_data):
    try:
        data = {
            'packet_size': user_data[0][0],
            'request_rate': user_data[0][1]
        }
        response = requests.post("http://127.0.0.1:5000/predict", json=data)

        if response.status_code == 200:
            result = response.json()
            return result.get('prediction')
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error in call_model_api: {e}")
        return None

def run_model():
    global last_request_time  
    while True:
        try:
            if last_request_time:
                user_data = np.array([[0, 0]])  # TODO: Need to change the array to something else to avoid index out of bounds error in terminal
                user_data = user_data.reshape((1, 1, 2))

                predicted_label = call_model_api(user_data)

                if predicted_label is not None and predicted_label in label_data:
                    sampled_data = label_data[predicted_label]
                    sampled_packet_size, sampled_request_rate = sampled_data[np.random.choice(sampled_data.shape[0])]
                    print(f"Predicted Label: {predicted_label}, Packet Size: {sampled_packet_size}, Request Rate: {sampled_request_rate}")
                else:
                    print(f"No valid prediction or data found for label: {predicted_label}")

            time.sleep(5)
        except Exception as e:
            print(f"Error in run_model: {e}")

@app.before_request
def before_request():
    global last_request_time
    last_request_time = time.time()

if __name__ == '__main__':
    model_thread = Thread(target=run_model)
    model_thread.daemon = True  
    model_thread.start()

    app.run(debug=True)
