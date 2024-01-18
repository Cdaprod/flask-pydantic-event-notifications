import json
import psycopg2
from typing import List, Dict, Any, Optional
from flask import Flask, jsonify, request
from minio import Minio
from pydantic import BaseModel, ValidationError



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

class OwnerIdentity(BaseModel):
    principalId: str

class Bucket(BaseModel):
    arn: str
    name: str
    ownerIdentity: OwnerIdentity

class UserMetadata(BaseModel):
    content_type: str

class Object(BaseModel):
    key: str
    eTag: str
    size: int
    sequencer: str
    contentType: str
    userMetadata: UserMetadata

class S3(BaseModel):
    bucket: Bucket
    object: Object
    configurationId: str
    s3SchemaVersion: str

class Source(BaseModel):
    host: str
    port: Optional[str]
    userAgent: str

class ResponseElements(BaseModel):
    x_amz_id_2: str
    x_amz_request_id: str
    x_minio_deployment_id: str
    x_minio_origin_endpoint: str

class RequestParameters(BaseModel):
    region: Optional[str]
    principalId: str
    sourceIPAddress: str

class Record(BaseModel):
    s3: S3
    source: Source
    awsRegion: Optional[str]
    eventName: str
    eventTime: str
    eventSource: str
    eventVersion: str
    userIdentity: OwnerIdentity
    responseElements: ResponseElements
    requestParameters: RequestParameters

class Event(BaseModel):
    Records: List[Record]

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

@app.route('/minio-event', methods=['POST'])
def handle_minio_event():
    event_data = request.json
    try:
        # Parse the event data using Pydantic
        event = Event.parse_obj(event_data)

        # Open a new database connection
        with psycopg2.connect(
            host=postgres_config.host,
            port=postgres_config.port,
            user=postgres_config.user,
            password=postgres_config.password,
            dbname=postgres_config.database
        ) as pg_conn:

            with pg_conn.cursor() as cur:
                for record in event.Records:
                    object_key = record.s3.object.key
                    json_data = json.dumps(record.dict())

                    cur.execute("""
                        INSERT INTO events (key, value) 
                        VALUES (%s, %s)
                        ON CONFLICT (key) 
                        DO UPDATE SET value = EXCLUDED.value;
                        """, (object_key, json_data))
                # Commit is automatic due to the context manager

        return "Event processed", 200

    except ValidationError as e:
        print(f"Validation error: {e}")
        return "Invalid event data", 400
    except Exception as e:
        print(f"Error: {e}")
        # No need to explicitly roll back, it's handled by the context manager
        return "Internal server error", 500

@app.route('/hello', methods=['GET'])
def hello():
    return "Hello MinIO!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
    

