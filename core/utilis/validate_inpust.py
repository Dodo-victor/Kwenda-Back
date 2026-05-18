import phonenumbers
import re
import bcrypt
from core.utilis.security import hash_password


class ValidateInputs:

    def __init__(self) -> None:
        pass

    @staticmethod
    def validate_email(email: str) -> str | bool:
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.fullmatch(pattern, email) :
            return email
        else: 
            return False

    @staticmethod
    def validate_phone_number(phone_number: int) -> int | bool:
        phone_str = str(phone_number)
        phone_parsed = phonenumbers.parse(number=phone_str, region="AO")
        validate_number = phonenumbers.is_valid_number(phone_parsed)
        if not validate_number:
            return False
        else:
            return phone_number

    @staticmethod
    def validate_password(password: str) -> str | bool:
        pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        )
        if re.fullmatch(pattern, password):
            return hash_password(password=password)
        else:
            return False

    @staticmethod
    def validate_bi(bi: str) -> str | bool:
        padrao_bi = r"^\d{9}[A-Z]{2}\d{3}$"

        if re.fullmatch(padrao_bi, bi):
            return bi
        else:
            return False
