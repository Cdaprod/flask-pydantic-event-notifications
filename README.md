# flask-pydantic-event-notifications


# Setup MC Commands for Python Webhook 
---

mc alias set myminio http://localhost:9000 minio minio123 --api S3v4

mc: Configuration written to `/Users/davidcannan/.mc/config.json`. Please update your access credentials.mc: Successfully created `/Users/davidcannan/.mc/share`.
mc: Initialized share uploads `/Users/davidcannan/.mc/share/uploads.json` file.mc: Initialized share downloads `/Users/davidcannan/.mc/share/downloads.json` file.Added `myminio` successfully.

---

mc admin config set myminio notify_webhook:1 endpoint="http://host.docker.internal:35000/event" queue_limit="0"

Successfully applied new settings.
Please restart your server 'mc admin service restart myminio'.
➜  ~ mc admin service restart myminio
Restart command successfully sent to `myminio`. Type Ctrl-C to quit or wait to follow the status of the restart process....
Restarted `myminio` successfully in 1 seconds

---

mc mb myminio/mybucket

Bucket created successfully `myminio/mybucket`.

---

mc event add myminio/mybucket arn:minio:sqs::1:webhook --event put,get,delete

---

mc event add myminio/mybucket arn:minio:sqs::1:webhook --event put,get,delete

Successfully added arn:minio:sqs::1:webhook

---
