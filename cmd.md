# Curl to Flask App to test Postgres table

```curl
curl -X POST http://localhost:5000/event \
-H "Content-Type: application/json" \
-d '{
    "Records": [
        {
            "eventName": "s3:ObjectCreated:Put",
            "s3": {
                "bucket": {
                    "name": "example-bucket",
                    "ownerIdentity": {
                        "principalId": "EXAMPLE"
                    },
                    "arn": "arn:aws:s3:::example-bucket"
                },
                "object": {
                    "key": "testfile.txt",
                    "size": 1024,
                    "eTag": "d41d8cd98f00b204e9800998ecf8427e",
                    "sequencer": "0055AED6DCD90281E5"
                }
            }
        }
    ]
}'
```

# Psql Table Creation 
OLD:
```
docker exec -it [POSTGRES_CONTAINER_ID] psql -U myuser -d postgres -c "CREATE TABLE bucket_events (id SERIAL PRIMARY KEY, event_name VARCHAR(255), bucket_name VARCHAR(255), object_key VARCHAR(255), key VARCHAR(255), value VARCHAR(255), sequencer VARCHAR(255), data JSONB);"
...
TABLE CREATED
```


# Mc to Creating Bucket
```
mc mb myminio/test
                        
Bucket created successfully `myminio/test`.
```

# For notify_postgres
```
mc admin config set myminio notify_postgres:1 connection_string="user=myuser password=mypassword host=postgres dbname=postgres port=5432 sslmode=disable" table="bucket_events" format="namespace"
...
Successfully applied new settings.
Please restart your server 'mc admin service restart myminio'.
```

# For notify_webhook
```
mc admin config set myminio notify_webhook:1 endpoint="http://host.docker.internal:5000/event" queue_limit="10" auth_token=""

Successfully applied new settings.
Please restart your server 'mc admin service restart myminio'.
```

# Restart MinIO
```
mc admin service restart myminio

Restart command successfully sent to `myminio`. Type Ctrl-C to quit or wait to follow the status of the restart process.
...
Restarted `myminio` successfully in 1 seconds
```

# Update Bucket with notify_webhook event 
``` 
mc event add myminio/mybucket arn:minio:sqs::1:webhook --event put,get,delete

Successfully added arn:minio:sqs::1:webhook
``` 

```
mc event list myminio/mybucket
arn:minio:sqs::1:webhook
...
s3:ObjectCreated:*,s3:ObjectAccessed:*,s3:ObjectRemoved:*   Filter:
```

```
mc cp event-test.txt myminio/mybucket
...
event-test.txt: 31 B / 31 B ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 818 B/s 0s
```


---

# For /minio-event (aws aligned)

FLASK WEBHOOK
```
from flask import Flask, request
import psycopg2
import json
from datetime import datetime

# Flask app initialization
app = Flask(__name__)

# Database connection setup
def get_db_connection():
    return psycopg2.connect(
        host='localhost',  # Adjust as needed
        port=5432,         # Adjust as needed
        user='myuser',     # Adjust as needed
        password='mypassword',  # Adjust as needed
        dbname='postgres'  # Adjust as needed
    )

# Route for handling MinIO events
@app.route('/minio-event', methods=['POST'])
def handle_minio_event():
    event_data = request.json
    conn = get_db_connection()

    for record in event_data['Records']:
        # Extract and transform data from the event record
        event_name = record['eventName']
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        size = record['s3']['object'].get('size')
        eTag = record['s3']['object'].get('eTag')
        sequencer = record['s3']['object'].get('sequencer')
        event_time = datetime.fromisoformat(record['eventTime'].rstrip('Z'))
        aws_region = record.get('awsRegion')
        ip_address = record['requestParameters']['sourceIPAddress']
        request_id = record['responseElements'].get('x-amz-request-id')
        user_identity = json.dumps(record['userIdentity'])

        # Additional data can include any extra fields in the event record
        additional_data = json.dumps({k: v for k, v in record.items() if k not in 
                                      ["eventName", "s3", "eventTime", "awsRegion", 
                                       "requestParameters", "responseElements", "userIdentity"]})

        # Insert event data into PostgreSQL
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (
                    event_name, bucket_name, object_key, size, eTag, sequencer,
                    event_time, aws_region, ip_address, request_id, user_identity,
                    additional_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    event_name, bucket_name, object_key, size, eTag, sequencer,
                    event_time, aws_region, ip_address, request_id, user_identity,
                    additional_data
                )
            )
            conn.commit()
    conn.close()
    return "Event processed", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
``` 

NEW TABLE (aws aligned):
```
docker exec -it postgres-container psql -U myuser -d postgres -c "CREATE TABLE IF NOT EXISTS events (id SERIAL PRIMARY KEY, event_name VARCHAR(255), bucket_name VARCHAR(255), object_key VARCHAR(255), size BIGINT, eTag VARCHAR(255), sequencer VARCHAR(255), event_time TIMESTAMP WITH TIME ZONE, aws_region VARCHAR(255), ip_address VARCHAR(255), request_id VARCHAR(255), user_identity JSONB, additional_data JSONB);"
```

SET WEBHOOK 
```
mc admin config set myminio notify_webhook:1 endpoint="http://flaskapp:5000/minio-event" queue_limit="10"
mc admin service restart myminio
```

# KEY AND VALUE ONLY

Flask Webhook with Simplified Pydantic Model

```
from flask import Flask, request
import psycopg2
from pydantic import BaseModel
import json

# Flask app initialization
app = Flask(__name__)

# Pydantic model for simplified event data
class EventData(BaseModel):
    key: str
    value: json

# Database connection setup
def get_db_connection():
    return psycopg2.connect(
        host='localhost',      # Adjust as needed
        port=5432,             # Adjust as needed
        user='myuser',         # Adjust as needed
        password='mypassword', # Adjust as needed
        dbname='postgres'      # Adjust as needed
    )

# Route for handling MinIO events
@app.route('/minio-event', methods=['POST'])
def handle_minio_event():
    event_data = request.json
    conn = get_db_connection()

    # Process and insert each event record
    for record in event_data['Records']:
        event = EventData(key=record['s3']['object']['key'], value=record)
        
        with conn.cursor() as cur:
            cur.execute("INSERT INTO events (key, value) VALUES (%s, %s)", 
                        (event.key, json.dumps(event.value)))
            conn.commit()
    conn.close()
    return "Event processed", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

New Table Schema:

```
docker exec -it postgres-container psql -U myuser -d postgres -c "CREATE TABLE IF NOT EXISTS events (id SERIAL PRIMARY KEY, key VARCHAR(255), value JSONB);"
```

Set Webhook in MinIO:

```
mc admin config set myminio notify_webhook:1 endpoint="http://flaskapp:5000/minio-event" queue_limit="10"
mc admin service restart myminio
```

This setup focuses on the essentials: capturing the key and value of the event and storing them in the PostgreSQL database. 