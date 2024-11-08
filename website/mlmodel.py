import os
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import load_model
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

# Set up logging for error tracking
logging.basicConfig(level=logging.INFO)

# Load model and data pathsChange this directory if needed
MODEL_PATH = os.path.join('mlmodel.keras')  
DATA_FILE = os.path.join('network_traffic_data.csv')

# Categories from dataset
CATEGORIES = ['normal', 'DDOS', 'port_scan']

# Initialize global model variable
model = None
label_encoder = LabelEncoder()
label_encoder.fit(CATEGORIES)
scaler = StandardScaler()

# Load model and scaler
try:
    logging.info(f"Loading model from {MODEL_PATH}")
    model = load_model(MODEL_PATH)  # Load pre-trained model
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")

# Load dataset for scaling purposes
try:
    data = pd.read_csv(DATA_FILE)
    scaler.fit(data[['packet_size', 'request_rate']])
except Exception as e:
    logging.error(f"Error loading or fitting scaler: {e}")

# Preprocess input data
def preprocess_data(input_data):
    input_scaled = scaler.transform(input_data)
    input_scaled = np.reshape(input_scaled, (input_scaled.shape[0], 1, input_scaled.shape[1]))  # Reshape for LSTM
    return input_scaled

# Function to predict using the pre-trained model
def make_prediction(input_data):
    try:
        if model is None:
            logging.error("Model is not loaded. Cannot make predictions.")
            return {"error": "Model is not loaded."}, 500
        
        # Ensure input_data is in the right shape
        if len(input_data) == 0 or len(input_data[0]) != 2:
            logging.error("Invalid input data shape. Expected shape (batch_size, 2).")
            return {"error": "Invalid input data shape."}, 400
        
        input_scaled = preprocess_data(input_data)
        predictions = model.predict(input_scaled)

        # Get predicted class index and confidence scores
        predicted_classes = np.argmax(predictions, axis=1).astype(int)
        confidence_scores = np.max(predictions, axis=1)

        # Prepare response
        response = []
        for index in range(len(predicted_classes)):
            label = label_encoder.inverse_transform([predicted_classes[index]])[0]
            confidence = confidence_scores[index]
            response.append({'label': label, 'confidence': float(confidence)})  # Convert confidence to float for JSON serialization
        
        return {"predictions": response}, 200  # Return predictions with 200 status code
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return {"error": str(e)}, 500  # Return error with 500 status code

# # Sample test input for making a prediction
# if __name__ == "__main__":
#     # Sample test input (adjust as needed to match your dataset columns)
#     sample_data = pd.DataFrame({'packet_size': [1000], 'request_rate': [15]})

#     # Make a prediction
#     prediction = make_prediction(sample_data.values)
#     print("Prediction:", prediction)
