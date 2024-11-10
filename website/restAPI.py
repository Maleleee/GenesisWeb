from flask import Blueprint, request, jsonify
import logging
from .mlmodel import make_prediction

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/predict', methods=['POST'])
def predict():
    """Endpoint to predict the label based on packet size and request rate."""
    try:
        user_data = request.get_json()  # Get JSON data from the request
        
        # Input validation
        packet_size = user_data.get('packet_size')
        request_rate = user_data.get('request_rate')

        if packet_size is None or request_rate is None:
            return jsonify({'error': 'Invalid input data: packet_size and request_rate are required.'}), 400
        
        if not isinstance(packet_size, (int, float)) or not isinstance(request_rate, (int, float)):
            return jsonify({'error': 'Invalid input data: packet_size and request_rate must be numeric.'}), 400

        # Call the prediction function
        predicted_label = make_prediction([[packet_size, request_rate]])

        if predicted_label:
            return jsonify({'prediction': predicted_label}), 200
        else:
            logger.error("Prediction failed: no label returned.")
            return jsonify({'error': 'Prediction failed: no label returned.'}), 500

    except Exception as e:
        logger.exception("Error in predict: %s", e)
        return jsonify({'error': 'An error occurred during prediction.'}), 500
