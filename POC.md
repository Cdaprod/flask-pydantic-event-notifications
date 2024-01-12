# Event-Driven Architecture: MinIO Integrations - Automating Bucket Events with Python Webhooks

### Proof of Concept Summary for Blog Review
 
This article presents a comprehensive Proof of Concept (PoC) that demonstrates the integration of Flask, a micro web framework, with MinIO, an object storage server, and PostgreSQL, a relational database, for efficient event data handling and storage. The primary goal of this PoC is to illustrate how these three technologies can be seamlessly combined to build a robust, scalable system capable of managing event data in real-time, and how the Pydantic Library enables clients and dataclasses to be written in a clean and concise manner. 

## Key components of this integration include:

- Python Classes: Leveraged for data validation and settings management, ensuring robust data handling. We’ll do this seamlessly using the Pydantic module.
- MinIO Client Initialization: Demonstrates the use of MinIO for object storage, essential for handling large volumes of data.
- PostgreSQL Database Integration: Showcases how to reliably store and manage structured event data.
- Flask Web Server: Serves as the backbone of the application, handling HTTP requests and routing them to the appropriate processing functions.

## The PoC also explores:

- Event Processing and Serialization: Critical for ensuring that data is correctly formatted and stored.
- Error Handling Mechanisms: Demonstrating robustness and reliability of the system in adverse conditions.
- Practical Application: Through the simulation of an event, we provide a real-world scenario that showcases the system’s capabilities.

The expected outcome of this PoC is to validate the feasibility and effectiveness of integrating Python, MinIO, and PostgreSQL for event data management. It is a compelling demonstration for developers and architects looking to build scalable and efficient applications using these technologies.

As we prepare this PoC for review, we aim to provide a detailed, practical example that not only showcases technical integration but also offers insights into its real-world applicability and scalability. This article will be an invaluable resource for professionals seeking to implement similar solutions in their projects or enterprises.

---

Setup the MinIO and Postgres Services with Docker Compose

We will begin by setting up a Python application and its environment. This involves deploying MinIO with docker compose and the services to be integrated. To set up MinIO with a Flask application, and a PostgreSQL using the MinIO blog-assets repository, execute the following commands.
```bash
git clone https://github.com/minio/blog-assets.git

cd flask-pydantic-event-notifications 

docker-compose up -d
```
Directory Structure 

```
/flask-pydantic-event-notifications
├── Dockerfile
├── app
│       └── main.py
├── docker-compose.yaml
└── event-test.txt
``` 

# Dockerfile for flaskapp

```
FROM python:3.8 
WORKDIR /app
COPY . .
RUN pip install Flask psycopg2-binary minio pydantic python-dotenv
EXPOSE 5000
ENV FLASK_ENV=development
CMD ["python", "app/main.py"]
```

# Write docker-compose.yaml to local directory

```python
version: '3.8'
services:
  Flaskapp: # This is where we can assign a hostname
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - minio
      - postgres

  minio:
    image: minio/minio
    environment:
      MINIO_ACCESS_KEY: minio
      MINIO_SECRET_KEY: minio123
    command: server /data
    ports:
      - "9000:9000"
    volumes:
      - minio_data:/data

  postgres:
    image: postgres:alpine
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  minio_data:
  postgres_data:
```

```
docker-compose up -f docker-compose.yaml
```
# Check if containers are running

```
docker ps -f name=minio
docker ps -f name=Flaskapp
docker ps -f name=postgres
```

CONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMES
0e113865e67e quay.io/minio/minio"/usr/bin/docker-entâ€¦" 4 months ago Up 4 hours 0.0.0.0:9000->9000/tcp, 0.0.0.0:9090->9090/tcp minio 
CONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMES
c580a2f2a48c postgres:alpine "docker-entrypoint.sâ€¦" 6 days ago Up 6 days 0.0.0.0:5432->5432/tcp postgres
# Create the table in the container

```
 docker exec -it flask-pydantic-event-notifications-postgres-1 psql -U myuser -d postgres -c "DROP TABLE IF EXISTS events; CREATE TABLE events (key TEXT PRIMARY KEY, value JSONB);"
DROP TABLE
CREATE TABLE
```

This is the output you should be expecting

`CREATE TABLE`

# Configuring Webhook with MC 

```
docker exec flask-pydantic-event-notifications-minio-1 mc alias set myminio http://localhost:9000 minio minio123

Added `myminio` successfully.
```

```
docker exec flask-pydantic-event-notifications-minio-1 mc admin config set myminio notify_webhook:1 endpoint="http://flaskapp:5000/event" queue_limit="10" comment="Webhook for Flask app"
```

# Set an alias

``` 
mc alias set myminio http://localhost:9000 minio minio123 --api S3v4
```
mc: Configuration written to `/Users/davidcannan/.mc/config.json`. Please update your access credentials.mc: Successfully created `/Users/davidcannan/.mc/share`.
mc: Initialized share uploads `/Users/davidcannan/.mc/share/uploads.json` file.mc: Initialized share downloads `/Users/davidcannan/.mc/share/downloads.json` file.Added `myminio` successfully.

# Create notify_webhook with host.docker.internal

``` 
mc admin config set myminio notify_webhook:1 endpoint="http://host.docker.internal:35000/minio-event" queue_limit="0"
```

Successfully applied new settings.
Please restart your server 'mc admin service restart myminio'.


# Restart MinIO

```
mc admin service restart myminio
```
Restart command successfully sent to `myminio`. Type Ctrl-C to quit or wait to follow the status of the restart process....
Restarted `myminio` successfully in 1 seconds


# Use alias to create bucket named mybucket 

```
mc mb myminio/mybucket
```
Bucket created successfully `myminio/mybucket`.

# Subscribe the bucket to the event for put, get, and delete

```
mc event add myminio/mybucket arn:minio:sqs::1:webhook --event put,get,delete
```
Successfully added arn:minio:sqs::1:webhook

# TIP: If you need to erase the remove an ARN to recreate it

```
mc event rm myminio/mybucket arn:minio:sqs::1:webhook
```
Successfully removed arn:minio:sqs::1:webhook

# List the event on the bucket

```
mc event list myminio/mybucket
```
arn:minio:sqs::1:webhook   s3:ObjectCreated:*,s3:ObjectAccessed:*,s3:ObjectRemoved:*   Filter:

# List the alias/bucket arn in --json

```
mc event list myminio/mybucket arn:minio:sqs::1:webhook --json
```
Returns the following webhooko configurations
{
 "status": "success",
 "id": "",
 "event": [
  "s3:ObjectCreated:*",
  "s3:ObjectAccessed:*",
  "s3:ObjectRemoved:*"
 ],
 "prefix": "",
 "suffix": "",
 "arn": "arn:minio:sqs::1:webhook"
}

# Watch the bucket from another terminal

```
mc watch myminio/mybucket
```

When next mc cp command completes for following will appear
[2024-01-11T22:22:22.523Z] 
7.4 KiB s3:ObjectCreated:Put http://localhost:9000/mybucket/cmd.md

# Copy something into the bucket

```
 mc cp cmd.md myminio/mybucket
```
Returns something like this:
...t-notifications-2/cmd.md: 7.40 KiB / 7.40 KiB ━━━━━━━━━━━━ 461.85 KiB/s 0s



# The API Development Code for Integrating Numerous Clients & Services with MinIO

Ive added lots of comments to outline each step for whoever is reading this:

```python
import json
import psycopg2
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

# Route for handling MinIO events without Py
@app.route('/minio-event', methods=['POST'])
def handle_minio_event():
    event_data = request.json
    try:
        with pg_conn.cursor() as cur:
            for record in event_data['Records']:
                try:
                    # Extract object key directly from record
                    object_key = record['s3']['object']['key']
                except KeyError as e:
                    print(f"Key error: {e}")
                    continue

                # Store the entire record as JSON
                json_data = json.dumps(record)

                cur.execute("""
                    INSERT INTO minio_events (key, value) 
                    VALUES (%s, %s)
                    ON CONFLICT (key) 
                    DO UPDATE SET value = EXCLUDED.value;
                    """, (object_key, json_data))
            pg_conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        pg_conn.rollback()
    finally:
        pg_conn.close()

    return "Event processed", 200

@app.route('/hello', methods=['GET'])
def hello():
    return "Hello MinIO!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
    

``` 
2024-01-11 18:36:34  * Serving Flask app 'main'
2024-01-11 18:36:34  * Debug mode: on
2024-01-11 18:36:34 WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
2024-01-11 18:36:34  * Running on all addresses (0.0.0.0)
2024-01-11 18:36:34  * Running on http://127.0.0.1:5000
2024-01-11 18:36:34  * Running on http://172.18.0.4:5000
2024-01-11 18:36:34 Press CTRL+C to quit
2024-01-11 18:36:34  * Restarting with stat
2024-01-11 18:36:34  * Debugger is active!
2024-01-11 18:36:34  * Debugger PIN: 118-680-527
2024-01-11 18:37:13 192.168.65.1 - - [11/Jan/2024 23:37:13] "GET / HTTP/1.1" 404 -
2024-01-11 18:37:13 192.168.65.1 - - [11/Jan/2024 23:37:13] "GET /favicon.ico HTTP/1.1" 404 -
2024-01-11 18:37:20 192.168.65.1 - - [11/Jan/2024 23:37:20] "GET /minio-event HTTP/1.1" 405 -
2024-01-11 18:37:24 192.168.65.1 - - [11/Jan/2024 23:37:24] "GET /hello HTTP/1.1" 200 -

# Viewing the Results

```
docker exec flask-pydantic-event-notifications-postgres-1 psql -U myuser -d postgres -c "SELECT * FROM events;"
```

id | event_type | data | event_time | key | value
----+---------------+---------------------------------------------------------------------------------+------------+-----+------- 
1 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
2 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
3 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
4 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
5 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
6 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
7 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
8 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
9 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
10 | file_uploaded | {"file_name": "example.txt", "file_size": "1024", "bucket_name": "test-bucket"} | | | 
(10 rows)

