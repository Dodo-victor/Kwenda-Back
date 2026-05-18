import random
import string

def generate_type_queue(type_senha: str, position: int = None) -> str | int:

    match type_senha:
        case "password":
            code = "".join(random.choices(string.digits, k=7))
            return code
        case "numeric":
            return position
        case _:
            raise ValueError("Invalid type_senha")
  