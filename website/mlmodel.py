import os
import numpy as np
import pandas as pd
import tensorflow as tf
from keras import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.utils import to_categorical
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Constants
BASE_DIR = r'C:\Users\User\Documents\GitHub\GenesisWeb\website'  # Directory where the CSV file is located
DATA_FILE = os.path.join(BASE_DIR, 'network_traffic_data.csv')  # Path to your CSV file
TEST_DIR = r'C:\Users\User\Documents\GitHub\GenesisWeb\website'

# Define the categories based on your dataset
CATEGORIES = ['normal', 'DDOS', 'port_scan', 'syn_flood', 'icmp_flood']

# Initialize the label encoder
label_encoder = LabelEncoder()
label_encoder.fit(CATEGORIES)

# Load and preprocess training data from the CSV file
def load_and_preprocess_data():
    data = pd.read_csv(DATA_FILE)  # Load the entire dataset
    print("Columns in CSV:", data.columns)  # Check the columns for verification

    # Extract features and labels
    features = data[['packet_size', 'request_rate']]  # Select relevant features
    labels = data['label']  # Use the 'label' column for labels

    # Encode the labels
    label_encoder = LabelEncoder()
    label_encoder.fit(labels)
    y = label_encoder.transform(labels)
    y_one_hot = to_categorical(y, num_classes=len(label_encoder.classes_))

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    X_scaled = np.reshape(X_scaled, (X_scaled.shape[0], 1, X_scaled.shape[1]))  # For LSTM input

    return X_scaled, y_one_hot, scaler, label_encoder

# Load combined test data from all categories
def load_combined_test_data(scaler, label_encoder):
    test_data = []
    test_labels = []
    files = [os.path.join(TEST_DIR, f) for f in os.listdir(TEST_DIR) if f.endswith('.csv')]
    for file_path in files:
        data = pd.read_csv(file_path)
        features = data[['packet_size', 'request_rate']]  # Select relevant features
        labels = data['label']  # Use the 'label' column for labels
        test_data.append(features)
        test_labels.extend(labels)

    # Check if test_data is not empty before concatenating
    if test_data:
        X_test = pd.concat(test_data, ignore_index=True)
        y_test = label_encoder.transform(test_labels)
        y_test_one_hot = to_categorical(y_test, num_classes=len(label_encoder.classes_))
        X_test_scaled = scaler.transform(X_test)
        X_test_scaled = np.reshape(X_test_scaled, (X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))  # For LSTM input
        return X_test_scaled, y_test_one_hot, y_test
    else:
        print("No test data found. Please ensure that the test data files are present in the TEST_DIR.")
        return None, None, None

# Define the LSTM model
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

# Training and validation
X_train, y_train, scaler, label_encoder = load_and_preprocess_data()
model = create_model((X_train.shape[1], X_train.shape[2]), len(label_encoder.classes_))
history = model.fit(X_train, y_train, epochs=50, validation_split=0.3)

# Evaluate the model on combined test data
X_test, y_test_one_hot, y_test = load_combined_test_data(scaler, label_encoder)
loss, accuracy = model.evaluate(X_test, y_test_one_hot)
print(f"Combined test accuracy: {accuracy * 100:.2f}%")

# Detailed evaluation metrics
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)
print(classification_report(y_test, y_pred_classes, target_names=label_encoder.classes_))

# Confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred_classes)
plt.figure(figsize=(10, 8))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="YlGnBu", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.show()

# Optionally save the model
model.save(r'C:\Users\User\Documents\GitHub\GenesisWeb\website\mlmodel.h5')