# validators.py

import phonenumbers
from wtforms.validators import ValidationError

def PhoneNumberValidator(form, field):
    try:
        input_number = phonenumbers.parse(field.data, None)  # 'None' lets the library detect the region
        if not phonenumbers.is_valid_number(input_number):
            raise ValidationError('Invalid phone number.')
    except phonenumbers.NumberParseException:
        raise ValidationError('Invalid phone number format.')
