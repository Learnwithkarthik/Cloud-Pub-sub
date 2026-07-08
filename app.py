import base64
import json
import os
from datetime import datetime, timezone

import functions_framework
from google.cloud import storage


@functions_framework.cloud_event
def process_order_event(cloud_event):
    data = cloud_event.data
    message = data.get("message", {})

    encoded_data = message.get("data", "")

    if not encoded_data:
        print("No Pub/Sub message data found")
        return

    decoded_data = base64.b64decode(encoded_data).decode("utf-8")
    order = json.loads(decoded_data)

    print("Received order event:")
    print(order)

    output_bucket_name = os.environ.get("OUTPUT_BUCKET")
    service_name = os.environ.get("SERVICE_NAME", "notification")
    output_folder = os.environ.get("OUTPUT_FOLDER", "notifications")

    if not output_bucket_name:
        raise ValueError("OUTPUT_BUCKET environment variable is not set")

    order_id = order.get("order_id", "unknown-order")
    customer = order.get("customer", "unknown-customer")
    item = order.get("item", "unknown-item")
    amount = order.get("amount", "0")

    output_content = f"""
PUB/SUB SUBSCRIBER OUTPUT

Service Name: {service_name}
Action: Notification sent

Order ID: {order_id}
Customer: {customer}
Item: {item}
Amount: {amount}

Processed Time: {datetime.now(timezone.utc).isoformat()}

Explanation:
This file was created by the Notification Worker.
The worker received the order event from Pub/Sub topic order-events.
"""

    storage_client = storage.Client()
    bucket = storage_client.bucket(output_bucket_name)

    file_name = f"{output_folder}/{order_id}-{service_name}.txt"
    blob = bucket.blob(file_name)
    blob.upload_from_string(output_content)

    print(f"Output created: gs://{output_bucket_name}/{file_name}")
