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

# Define your base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of this file
DATA_FILE = os.path.join(BASE_DIR, 'network_traffic_data.csv')  # Path to the CSV file
CATEGORIES = ['normal', 'DDOS', 'port_scan'] # Categories from dataset.

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

# Load and preprocess data for training
def load_and_preprocess_data():
    data = pd.read_csv(DATA_FILE)
    features = data[['packet_size', 'request_rate']]
    labels = data['label'].values
    
    # Initialize encoder and scaler
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)
    y_one_hot = to_categorical(y, num_classes=len(CATEGORIES))
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    X_scaled = np.reshape(X_scaled, (X_scaled.shape[0], 1, X_scaled.shape[1]))  # For LSTM
    return X_scaled, y_one_hot, scaler

# Create LSTM model
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