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
mc admin config set myminio notify_webhook:1 endpoint="http://host.docker.internal:5000/event" queue_limit="0" auth_token=""

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