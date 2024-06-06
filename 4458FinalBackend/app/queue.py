from azure.storage.queue import QueueServiceClient
import base64
import json

account_name = "userqueue"
account_key = 'wohwJXz+j0FbjM8WyagClJyka2DUwZw+msu44llMuKadudRlo56+9RxzCi1yKLVltaYSHuUmKroe+ASt7DNFuQ=='
queue_name = "milesuser"


def connect():
    # Create a QueueServiceClient
    queue_service_client = QueueServiceClient(account_url=f"https://{account_name}.queue.core.windows.net", credential=account_key)

    # Create a QueueClient
    queue_client = queue_service_client.get_queue_client(queue_name)

    return queue_client

def addMessagetoQueue(jsonFormatMessage):
    queue_client = connect()
    json_format_message = json.dumps(jsonFormatMessage)
    # Encode the message content (assuming it's a string)
    encoded_message = base64.b64encode(json_format_message.encode()).decode('utf-8')
    queue_client.send_message(encoded_message)
    