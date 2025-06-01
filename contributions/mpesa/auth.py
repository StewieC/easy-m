import requests
from django.conf import settings

def get_access_token():
    url = settings.MpesaConfig['AUTH_URL']
    credentials = f"{settings.MpesaConfig['CONSUMER_KEY']}:{settings.MpesaConfig['CONSUMER_SECRET']}"
    encoded_credentials = credentials.encode('utf-8')
    base64_credentials = encoded_credentials.encode('base64').decode('utf-8').replace('\n', '')
    headers = {
        'Authorization': f'Basic {base64_credentials}',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    raise Exception(f"Failed to get access token: {response.text}")