from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship

# ML imports
import os
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.utils import to_categorical
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Define your base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of this file
DATA_FILE = os.path.join(BASE_DIR, 'network_traffic_data.csv')  # Path to the CSV file
CATEGORIES = ['normal', 'DDOS', 'port_scan', 'syn_flood', 'icmp_flood']

# Initialize label encoder
label_encoder = LabelEncoder()
label_encoder.fit(CATEGORIES)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    is_admin = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Float, default=0.0)
    transactions = relationship('Transaction', backref='user')

class LoginEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    status = db.Column(db.String(64)) # online or offline

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction_date = db.Column(db.DateTime(timezone=True), default=func.now())
    transaction_type = db.Column(db.Boolean)  # True = deposit, False = withdraw
    amount = db.Column(db.Float)
    status = db.Column(db.Boolean)  # True = success, False = failed

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    endpoint = db.Column(db.String(100), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    packet_size = db.Column(db.Integer, default=0)
    request_rate = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    
    def __repr__(self):
        return f"<UserActivity {self.id}>"
    
    
#### MACHINE LEARNING MODEL SECTION ####

# Load and preprocess training data for the machine learning model
def load_and_preprocess_data():
    data = pd.read_csv(DATA_FILE)  # Load the entire dataset
    features = data[['packet_size', 'request_rate']]  # Relevant features
    labels = data['label'].values  # Ensure your CSV has a 'label' column

    y = label_encoder.transform(labels)
    y_one_hot = to_categorical(y, num_classes=len(CATEGORIES))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    X_scaled = np.reshape(X_scaled, (X_scaled.shape[0], 1, X_scaled.shape[1]))  # For LSTM input
    return X_scaled, y_one_hot, scaler

# Define the LSTM machine learning model
def create_model(input_shape, num_classes):
    model = Sequential([
        LSTM(64, input_shape=input_shape, return_sequences=True),
        Dropout(0.3),
        LSTM(32, return_sequences=False),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Predict based on input data
def make_prediction(input_data):
    # Load and preprocess the input data
    X_train, y_train, scaler = load_and_preprocess_data()

    # Create and train the model
    model = create_model((X_train.shape[1], X_train.shape[2]), len(CATEGORIES))
    model.fit(X_train, y_train, epochs=50, validation_split=0.3)

    # Use the scaler to transform the input data
    input_scaled = scaler.transform(input_data[['packet_size', 'request_rate']])
    input_scaled = np.reshape(input_scaled, (input_scaled.shape[0], 1, input_scaled.shape[1]))

    # Predict the class of the input data
    predictions = model.predict(input_scaled)
    predicted_class = np.argmax(predictions, axis=1)
    predicted_label = label_encoder.inverse_transform(predicted_class)[0]

    return predicted_label