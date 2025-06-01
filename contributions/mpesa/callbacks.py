import json
import logging
from django.core.exceptions import ObjectDoesNotExist
from ..models import Contribution

logger = logging.getLogger(__name__)

def process_callback(raw_data):
    try:
        data = json.loads(raw_data.decode('utf-8'))
        logger.info(f"Callback data received: {data}")
        
        if 'Body' in data and 'stkCallback' in data['Body']:
            callback_data = data['Body']['stkCallback']
            result_code = callback_data.get('ResultCode')
            transaction_id = callback_data.get('MerchantRequestID')
            amount = callback_data.get('CallbackMetadata', {}).get('Item', [{}])[0].get('Value')
            phone_number = callback_data.get('CallbackMetadata', {}).get('Item', [{}])[3].get('Value')

            if result_code == 0:
                status = 'Success'
            else:
                status = 'Failed'

            try:
                contribution = Contribution.objects.get(transaction_id=transaction_id)
                contribution.status = status
                contribution.save()
                logger.info(f"Updated contribution {transaction_id} with status {status}")
            except ObjectDoesNotExist:
                logger.error(f"No contribution found for transaction ID {transaction_id}")
                # Optionally create a new contribution if not found (for testing)
                group_id = int(callback_data.get('AccountReference').split('_')[1]) if 'AccountReference' in callback_data else None
                if group_id:
                    Contribution.objects.create(
                        group_id=group_id,
                        user_id=1,  # Default user ID (update based on your logic)
                        amount=amount,
                        phone_number=phone_number,
                        transaction_id=transaction_id,
                        status=status
                    )
                    logger.info(f"Created new contribution for transaction ID {transaction_id}")
        else:
            logger.warning("Unexpected callback format: %s", data)
    except Exception as e:
        logger.error(f"Error processing callback: {str(e)}")