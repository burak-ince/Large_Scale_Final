from flask import Flask,request
from azure.storage.queue import QueueServiceClient
import base64,json
from app import app
import os
from app.mailsender import sendEmailToNewUser
from dotenv import load_dotenv


load_dotenv()

account_name = "userqueue"
account_key = os.getenv('AZURE_ACCOUNT_KEY')
queue_name = "milesuser"

def connect():
    # Create a QueueServiceClient
    queue_service_client = QueueServiceClient(account_url=f"https://{account_name}.queue.core.windows.net", credential=account_key)

    # Create a QueueClient
    queue_client = queue_service_client.get_queue_client(queue_name)

    return queue_client

def dequeue_message():
    # Connect to the queue
    queue_client = connect()

    # Dequeue a message
    messages = queue_client.receive_messages()
    for message in messages:
        decoded_message = decode_message(message.content)
        email = decoded_message.get('email')
        sendEmailToNewUser(email,"Welcome to MilesSmiles")
    return "Service Worked Everything is Fine"

def decode_message(encoded_message):
    try:
        # Decode base64 and parse JSON
        decoded_message = base64.b64decode(encoded_message).decode('utf-8')
        
        return json.loads(decoded_message)
    except (ValueError, UnicodeDecodeError) as e:
        print(f"Error decoding message: {str(e)}")
        return None
    
@app.route('/',methods = ['GET','POST'])
def hello_world():
    if request.method == 'GET':
        return 'Not A Trigger'
    else:
        response = dequeue_message()
        return response

@app.route('/check')
def check():
    return 'APP IS WORKING'
