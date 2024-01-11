from flask import Flask, request, jsonify
from minio import Minio
from pydantic import BaseModel
import psycopg2
import json

# Pydantic configuration class for MinIO client
class MinioClientConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool = False

# Pydantic configuration class for PostgreSQL client
class PostgresClientConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str

# Pydantic class for MinIO event data structure
class MinioEventData(BaseModel):
    event_name: str
    bucket_name: str
    object_key: str
    size: int
    eTag: str
    sequencer: str

from flask import Flask, request, jsonify
from minio import Minio
import psycopg2
import json

# Initialize configuration instances
minio_config = MinioClientConfig(
    endpoint='minio:9000', 
    access_key='minio', 
    secret_key='minio123'
)

postgres_config = PostgresClientConfig(
    host='postgres', 
    port=5432, 
    user='myuser', 
    password='mypassword', 
    database='postgres'
)

# Initialize MinIO and PostgreSQL clients
minio_client = Minio(
    minio_config.endpoint, 
    access_key=minio_config.access_key, 
    secret_key=minio_config.secret_key,
    secure=minio_config.secure
)

pg_conn = psycopg2.connect(
    host=postgres_config.host,
    port=postgres_config.port,
    user=postgres_config.user,
    password=postgres_config.password,
    dbname=postgres_config.database
)

# Flask app initialization
app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello_minio():
    return "Hello MinIO!"
    
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

# Route for handling MinIO events
@app.route('/event', methods=['POST'])
def handle_event():
    event_data = request.json
    for record in event_data['Records']:
        event = MinioEventData(
            event_name=record['eventName'],
            bucket_name=record['s3']['bucket']['name'],
            object_key=record['s3']['object']['key'],
            size=record['s3']['object'].get('size', 0),
            eTag=record['s3']['object'].get('eTag', ''),
            sequencer=record['s3']['object'].get('sequencer', '')
        )
        process_event(event)
    return "Event processed"

# Function to process events
def process_event(event: MinioEventData):
    json_data = event.json()

    # Insert event data into PostgreSQL
    try:
        with pg_conn.cursor() as cur:
            cur.execute("INSERT INTO bucket_events (event_name, bucket_name, object_key, sequencer, data) VALUES (%s, %s, %s, %s, %s)", 
                        (event.event_name, event.bucket_name, event.object_key, event.sequencer, json_data))
            pg_conn.commit()
    except Exception as e:
        pg_conn.rollback()
        print(f"Error processing event: {e}")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
