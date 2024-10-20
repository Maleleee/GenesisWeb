import os
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import load_model
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Load model and data paths 
BASE_DIR = r'C:\Users\User\Documents\GitHub\GenesisWeb' # Change this directory where the folder will be at your PC
MODEL_PATH = os.path.join(BASE_DIR, 'mlmodel.h5')  
DATA_FILE = os.path.join(BASE_DIR, 'network_traffic_data.csv')

# Categories from dataset
CATEGORIES = ['normal', 'DDOS', 'port_scan']

# Initialize label encoder and scaler
label_encoder = LabelEncoder()
label_encoder.fit(CATEGORIES)
scaler = StandardScaler()

# Load model and scaler
model = load_model(MODEL_PATH)  # Load pre-trained model
print("Model loaded successfully.")

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
