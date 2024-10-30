import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model  # Updated import
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Load model and data paths 
BASE_DIR = r'C:\Users\User\Documents\GitHub\GenesisWeb'  # Change this directory if needed
MODEL_PATH = os.path.join(BASE_DIR, 'mlmodel.h5')  
DATA_FILE = os.path.join(BASE_DIR, 'network_traffic_data.csv')

# Categories from dataset
CATEGORIES = ['normal', 'DDOS', 'port_scan']

# Initialize label encoder and scaler
label_encoder = LabelEncoder()
label_encoder.fit(CATEGORIES)
scaler = StandardScaler()

# Load model and scaler
try:
    model = load_model(MODEL_PATH)  # Load pre-trained model
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

# Load dataset for scaling purposes
data = pd.read_csv(DATA_FILE)
scaler.fit(data[['packet_size', 'request_rate']])

# Preprocess input data
def preprocess_data(input_data):
    input_scaled = scaler.transform(input_data)
    input_scaled = np.reshape(input_scaled, (input_scaled.shape[0], 1, input_scaled.shape[1]))  # For LSTM
    return input_scaled

# Function to predict using the pre-trained model
def make_prediction(input_data):
    input_scaled = preprocess_data(input_data)
    predictions = model.predict(input_scaled)

    # Get predicted class index and convert to native Python int for JSON serialization
    predicted_classes = np.argmax(predictions, axis=1).astype(int)
    
    # Return the label-encoded classes as a list
    return label_encoder.inverse_transform(predicted_classes).tolist()  # Convert to list for JSON serialization 

# Sample test input for making a prediction
if __name__ == "__main__":
    # Sample test input (adjust as needed to match your dataset columns)
    sample_data = pd.DataFrame({'packet_size': [1000], 'request_rate': [15]})
    
    # Make a prediction
    try:
        prediction = make_prediction(sample_data)
        print("Prediction:", prediction)
    except Exception as e:
        print(f"Error during prediction: {e}")
