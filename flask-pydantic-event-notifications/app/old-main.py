from pydantic import BaseModel
from flask import Flask, request
from minio import Minio
import psycopg2
import json

# Pydantic configuration class for MinIO client
class MinioClientConfig(BaseModel):
    endpoint: str = '192.168.0.25:9000'  # Using container hostname
    access_key: str = 'minio'
    secret_key: str = 'minio123'

# Pydantic configuration class for PostgreSQL client
class PostgresClientConfig(BaseModel):
    host: str = 'localhost'  # Using container hostname
    port: int = 5432
    user: str = 'myuser'
    password: str = 'mypassword'
    database: str = 'postgres'

# Pydantic class for event structure
class Event(BaseModel):
    event_type: str
    data: dict

# Create an instance of MinioClientConfig
minio_config = MinioClientConfig()

# Initialize MinIO client using the instance
minio_client = Minio(minio_config.endpoint, 
                     access_key=minio_config.access_key, 
                     secret_key=minio_config.secret_key)

# Create an instance of PostgresClientConfig
postgres_config = PostgresClientConfig()

# Initialize PostgreSQL connection using the instance
pg_conn = psycopg2.connect(
    host=postgres_config.host,
    port=postgres_config.port,
    user=postgres_config.user,
    password=postgres_config.password,
    dbname=postgres_config.database)

# Flask app initialization
app = Flask(__name__)

# Route for handling events
@app.route('/event', methods=['POST'])
def handle_event():
    event_data = request.json
    event = Event(**event_data)
    process_event(event)
    return "Event processed"

# Function to process events
def process_event(event: Event):
    # Serialize data to JSON
    json_data = json.dumps(event.data)

    # Process event and log data in PostgreSQL
    try:
        with pg_conn.cursor() as cur:
            cur.execute("INSERT INTO events (event_type, data) VALUES (%s, %s)", 
                        (event.event_type, json_data))
            pg_conn.commit()
            print("Event Notification for 'simulated_event_data' has been inserted successfully into 'Events' Table.")
    except Exception as e:
        pg_conn.rollback()  # Roll back the transaction in case of an error
        print(f"Error processing event: {e}")
       
 # Simulate an event for demonstration
simulated_event_data = {
    'event_type': 'file_uploaded',
    'data': {
        'file_name': 'example.txt',
        'file_size': '1024',
        'bucket_name': 'test-bucket'
    }
}

# Create Event instance with simulated data
simulated_event = Event(**simulated_event_data)

# Process the simulated event
process_event(simulated_event)

# Run the Flask app if this script is the main program
if __name__ == "__main__":
    app.run(debug=True, port=5000)