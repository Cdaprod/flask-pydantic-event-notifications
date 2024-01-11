from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/minio-webhook', methods=['POST'])
def log_minio_event():
    # Get JSON data sent by MinIO
    event_data = request.json

    # Convert the data to a formatted string for better readability
    formatted_data = json.dumps(event_data, indent=4)
    print("Received Event Data:", formatted_data)

    # For debugging purposes, you can also write to a file
    with open('minio_events.log', 'a') as log_file:
        log_file.write(formatted_data + '\n')

    return "Event logged", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)