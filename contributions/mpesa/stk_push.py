import requests
import json
from django.conf import settings
from datetime import datetime
import base64
from .auth import get_access_token

def initiate_stk_push(amount, phone_number, group_phone_number, group_id):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((settings.MpesaConfig['SHORTCODE'] + settings.MpesaConfig['PASSKEY'] + timestamp).encode()).decode('utf-8')
    
    payload = {
        "BusinessShortCode": settings.MpesaConfig['SHORTCODE'],
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(amount),
        "PartyA": phone_number,  # User's phone number
        "PartyB": group_phone_number,  # Group creator's phone number
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MpesaConfig['CALLBACK_URL'],
        "AccountReference": f"GROUP_{group_id}",
        "TransactionDesc": f"Contribution to Group {group_id}"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = settings.MpesaConfig['STK_PUSH_URL']
    response = requests.post(url, json=payload, headers=headers)
    return response.json()