# contributions/utils.py
from django.core.exceptions import ValidationError
import re

def validate_phone_number(value):
    if not re.match(r'^\+254[17]\d{8}$', value):
        raise ValidationError('Phone number must be in the format +2547XXXXXXXX or +2541XXXXXXXX.')