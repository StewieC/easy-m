import requests
import json
from datetime import datetime
import base64
from contributions.mpesa.auth import get_access_token  # Import the function to get access token
from easyM.settings import MpesaConfig  # Import directly from settings.py

def initiate_b2c_payment(amount, recipient_phone, initiator_phone):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    security_credential = base64.b64encode((MpesaConfig['SHORTCODE'] + MpesaConfig['PASSKEY'] + timestamp).encode()).decode('utf-8')

    payload = {
        "InitiatorName": "testapi",  # Replace with your initiator name from Daraja
        "SecurityCredential": security_credential,
        "CommandID": "BusinessPayment",
        "Amount": str(amount),
        "PartyA": MpesaConfig['SHORTCODE'],  # Your shortcode
        "PartyB": recipient_phone,  # Recipient's phone number
        "Remarks": "Merry-Go-Round Payout",
        "QueueTimeOutURL": MpesaConfig['CALLBACK_URL'],
        "ResultURL": MpesaConfig['CALLBACK_URL'],
        "Occasion": "Payout"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"  # Sandbox URL
    response = requests.post(url, json=payload, headers=headers)
    return response.json()