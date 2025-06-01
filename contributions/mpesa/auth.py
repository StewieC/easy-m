import requests
import base64  # Add this import
from easyM.settings import MpesaConfig
from easyM import settings

import logging
logger = logging.getLogger(__name__)

def get_access_token():
    url = settings.MpesaConfig['AUTH_URL']
    credentials = f"{settings.MpesaConfig['CONSUMER_KEY']}:{settings.MpesaConfig['CONSUMER_SECRET']}"
    encoded_credentials = credentials.encode('utf-8')  # Convert string to bytes
    base64_credentials = base64.b64encode(encoded_credentials).decode('utf-8').replace('\n', '')  # Base64 encode and convert back to string
    headers = {
        'Authorization': f'Basic {base64_credentials}',
    }
    logger.debug("Requesting access token with headers: %s", headers)
    response = requests.get(url, headers=headers)
    logger.debug("Access token response: %s", response.text)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    raise Exception(f"Failed to get access token: {response.text}")