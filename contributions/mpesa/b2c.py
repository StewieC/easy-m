import requests
import json
from django.conf import settings
from datetime import datetime
import base64
from .auth import get_access_token

def initiate_b2c_payment(amount, recipient_phone, initiator_phone):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    security_credential = base64.b64encode((settings.MpesaConfig['SHORTCODE'] + settings.MpesaConfig['PASSKEY'] + timestamp).encode()).decode('utf-8')
    
    payload = {
        "InitiatorName": "testapi",  # Replace with your initiator name from Daraja
        "SecurityCredential": security_credential,
        "CommandID": "BusinessPayment",
        "Amount": str(amount),
        "PartyA": settings.MpesaConfig['SHORTCODE'],  # Your shortcode
        "PartyB": recipient_phone,  # Recipient's phone number
        "Remarks": "Merry-Go-Round Payout",
        "QueueTimeOutURL": settings.MpesaConfig['CALLBACK_URL'],
        "ResultURL": settings.MpesaConfig['CALLBACK_URL'],
        "Occasion": "Payout"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"  # Sandbox URL
    response = requests.post(url, json=payload, headers=headers)
    return response.json()