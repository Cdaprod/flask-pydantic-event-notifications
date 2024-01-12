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
# Rewritten Proof of Concept Steps

## Step 1: Clone the Repository and Set Up the Environment

Clone the MinIO blog assets repository.

```
git clone https://github.com/minio/blog-assets.git
```

Change directory to the 'flask-pydantic-event-notifications' folder and bring up the Docker environment.

```
cd flask-pydantic-event-notifications 
docker-compose up -d
```

## Directory Structure Overview
The structure of the 'flask-pydantic-event-notifications' folder is as follows:

```
/flask-pydantic-event-notifications
├── Dockerfile
├── app
│   └── main.py
├── docker-compose.yaml
└── event-test.txt
``` 

## Dockerfile for Flask App

The Dockerfile used for setting up the Flask application:

```docker
FROM python:3.8 
WORKDIR /app
COPY . .
RUN pip install Flask psycopg2-binary minio pydantic python-dotenv
EXPOSE 5000
ENV FLASK_ENV=development
CMD ["python", "app/main.py"]
```

## Write docker-compose.yaml to Local Directory

Create a `docker-compose.yaml` file in your local directory with the following content:

```yaml
version: '3.8'
services:
  flaskapp: # This is where we can assign a hostname
    container_name: flaskapp
    build: .
    ports:
      - "35000:5000"
    depends_on:
      - minio
      - postgres

  minio:
    image: minio/minio
    container_name: minio
    environment:
      MINIO_ACCESS_KEY: minio
      MINIO_SECRET_KEY: minio123
    command: server /data
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  postgres:
    image: postgres:alpine
    container_name: postgres
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

## Bring Up the Docker Environment

Use the following command to start the Docker containers as defined in the `docker-compose.yaml` file.

```
docker-compose up -d
```

## Check if Containers are Running
Verify if the Docker containers for MinIO, Flaskapp, and Postgres are running using these commands:

```
docker ps -a
```

#### Expected:

Ooutput will display container IDs, images, commands, creation times, statuses, ports, and names.

## Create the Table in the Container
Execute this command to create a table in the Postgres container:

```
docker exec -it postgres psql -U myuser -d postgres -c "DROP TABLE IF EXISTS events; CREATE TABLE events (key TEXT PRIMARY KEY, value JSONB);"
```

#### Expect:

DROP TABLE
CREATE TABLE

## Configuring Webhook with MC 
Configure the webhook using MinIO Client (MC) with these commands:

```
docker exec minio mc alias set myminio http://localhost:9000 minio minio123
```

####Expect:

Added `myminio` successfully.

```
docker exec minio mc admin config set myminio notify_webhook:1 endpoint="http://flaskapp:5000/minio-event" queue_limit="10" comment="Webhook for Flask app"
```

#### Expect:

Successfully applied new settings.
Please restart your server 'mc admin service restart myminio'.

```
docker exec minio mc admin service restart myminio
```

#### Expect:

Restart command successfully sent to `myminio`. Type Ctrl-C to quit or wait to follow the status of the restart process....
Restarted `myminio` successfully in 1 seconds

## Create Bucket

Use these commands to create a bucket named 'mybucket' and subscribe it to specific events:

```
docker exec minio mc mb myminio/mybucket
```

#### Expect:

Bucket created successfully `myminio/mybucket`.

## Add Event to Newly Created Bucket

```
docker exec minio mc event add myminio/mybucket arn:minio:sqs::1:webhook --event put,get,delete
```

#### Expect:

Successfully added arn:minio:sqs::1:webhook

## List the Event on the Bucket
To list the event configuration on the bucket, use this command:

```
docker exec minio mc event list myminio/mybucket
```

#### Expect:

arn:minio:sqs::1:webhook   s3:ObjectCreated:*,s3:ObjectAccessed:*,s3:ObjectRemoved:*   Filter:

## List the Alias/Bucket ARN in JSON

For JSON formatted output of the event configuration, use:

```
docker exec minio mc event list myminio/mybucket arn:minio:sqs::1:webhook --json
```

#### Expect:

{
"status": "success",
"id": "",
"event": [
"s3:ObjectCreated:",
"s3:ObjectAccessed:",
"s3:ObjectRemoved:*"
],
"prefix": "",
"suffix": "",
"arn": "arn:minio:sqs::1:webhook"
}


## Copy Something into the Bucket

To copy a file into the bucket and trigger an event, use these commands:

```
docker exec minio bash -c "echo 'test' > cmd.md"

docker exec minio mc cp cmd.md myminio/mybucket
```

#### Expect:

...t-notifications-2/cmd.md: 7.40 KiB / 7.40 KiB ━━ 461.85 KiB/s 0s

## Check Flask App Logs for Event Notification

Upon successful copying of the file, check the Flask app logs for an entry indicating the receipt of an event notification.

#### Expect:
2024-01-12 12:50:23 172.18.0.3 - - [12/Jan/2024 17:50:23] "POST /minio-event HTTP/1.1" 200 

# Viewing the Results

To view the table in postgres using psql: 

```
docker exec flask-pydantic-event-notifications-postgres-1 psql -U myuser -d postgres -c "SELECT * FROM events;"
```

#### Expect:

```
   key | value
-------+---------------------
cmd.md | {"s3": {"bucket": {"arn": "arn:aws:s3:::mybucket", "name": "mybucket", "ownerIdentity": {"principalId": "minio"}}, "object": {"key": "cmd.md", "eTag": "d8e8fca2dc0f896fd7cb4cb0031ba249", "size": 5, "sequencer": "17A9AB4FA93B35D8", "contentType": "text/markdown", "userMetadata": {"content-type": "text/markdown"}}, "configurationId": "Config", "s3SchemaVersion": "1.0"}, "source": {"host": "127.0.0.1", "port": "", "userAgent": "MinIO (linux; arm64) minio-go/v7.0.66 mc/RELEASE.2024-01-11T05-49-32Z"}, "awsRegion": "", "eventName": "s3:ObjectCreated:Put", "eventTime": "2024-01-12T17:58:12.569Z", "eventSource": "minio:s3", "eventVersion": "2.0", "userIdentity": {"principalId": "minio"}, "responseElements": {"x-amz-id-2": "dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8", "x-amz-request-id": "17A9AB4FA9328C8F", "x-minio-deployment-id": "c3642fb7-ab2a-44a0-96cb-246bf4d18e84", "x-minio-origin-endpoint": "http://172.18.0.3:9000"}, "requestParameters": {"region": "", "principalId": "minio", "sourceIPAddress": "127.0.0.1"}}

(1 row)
```

