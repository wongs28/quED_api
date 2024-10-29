from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Fixed IP address of the device
DEVICE_IP = "192.168.1.100"  # Change this to your device's IP


@app.route('/get_device_data', methods=['GET'])
def get_device_data(param):
    """Fetch data from the device."""
    try:
        response = requests.get(f"http://{DEVICE_IP}:8080/?action=get&param={param}")  # Adjust endpoint as needed
        response.raise_for_status()  # Raise an error for bad responses
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/set_device_data', methods=['PUT'])
def set_device_data(param, value):
    """Send data to the device."""
    data = request.json  # Get JSON data from request body
    try:
        response = requests.post(f"http://{DEVICE_IP}:8080/?action=set&param={param}&value={value}", json=data)  # Adjust endpoint as needed
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
