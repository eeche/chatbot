import os
import ssl
import logging
from threading import Event
import requests
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from dotenv import load_dotenv

load_dotenv()

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

BOT_TOKEN = os.getenv('BOT_TOKEN')
SOCKET_TOKEN = os.getenv('SOCKET_TOKEN')
BOTNAME = 'BoB'

ALLOW_USERS = ['U07HAULKYJU', '']

SLACK_CLIENT = SocketModeClient(
    app_token=SOCKET_TOKEN,
    web_client=WebClient(token=BOT_TOKEN, ssl=ssl_context)
)

def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api" and req.payload["event"]["type"] == "message":
        event = req.payload["event"]
        user_id = event.get("user")
        message_text = event.get("text", "")
        channel = event.get("channel")
        
        # Ignore bot's own messages
        if user_id == client.web_client.auth_test()["user_id"]:
            return

        print(f"{user_id}: {message_text}")
        
        # Acknowledge the request
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        try:
            # Send a response message
            client.web_client.chat_postMessage(
                channel=channel,
                text=f"Received: {message_text}"
            )
            
            if user_id in ALLOW_USERS and message_text.lower().startswith('ioc'):
            # if user_id in ALLOW_USERS and 'ioc' in message_text.lower():
                print('IOC detected')
                client.web_client.reactions_add(
                    name="eyes",
                    channel=channel,
                    timestamp=event["ts"]
                )
                client.web_client.chat_postMessage(
                    channel=channel,
                    text="IOC detected. Further analysis required."
                )
        except Exception as e:
            logging.error(f"Error processing message: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        SLACK_CLIENT.socket_mode_request_listeners.append(process)
        SLACK_CLIENT.connect()
        Event().wait()
    except Exception as main_e:
        logging.error(f'Main function error: {main_e}')