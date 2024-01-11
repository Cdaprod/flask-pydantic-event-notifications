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

# Mc to MinIO for Configuring

```md

```