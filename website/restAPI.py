from flask import Blueprint, request, jsonify
from .mlmodel import make_prediction

api_bp = Blueprint('api', __name__)

@api_bp.route('/predict', methods=['POST'])
def predict():
    try:
        user_data = request.get_json()  # Get JSON data from the request
        packet_size = user_data.get('packet_size')
        request_rate = user_data.get('request_rate')

        if packet_size is None or request_rate is None:
            return jsonify({'error': 'Invalid input data'}), 400

        # Call the prediction function
        predicted_label = make_prediction([[packet_size, request_rate]])

        if predicted_label:
            return jsonify({'prediction': predicted_label}), 200
        else:
            return jsonify({'error': 'Prediction failed'}), 500
    except Exception as e:
        print(f"Error in predict: {e}")
        return jsonify({'error': 'An error occurred'}), 500
