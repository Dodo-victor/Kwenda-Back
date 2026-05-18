import jwt
from fastapi import HTTPException
from core.utilis.security import get_algorithm


ALGORITHM = get_algorithm()
SECRET_KEY = "password-key"


def gnerate_token(uid: str | dict) -> str:

    # header = {"alg": "HS256"}

    # token: str = jwt.encode( header=header, payload= {"uid": uid}, key=SECRET_KEY)

    if isinstance(uid, dict):
        token: str = jwt.encode(uid, SECRET_KEY, algorithm=ALGORITHM)
    else:
        token: str = jwt.encode({"uid": str(uid)}, SECRET_KEY, algorithm=ALGORITHM)
    print(token)
    return token


def verifield_token(token: str) -> bool | str | dict:
    print(token)
    try:
        decode_token = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_signature": False},
        )
        print(decode_token.get("uid"))
        if not decode_token:
            return False
        else:
            print("dentro do token", decode_token)
            return decode_token

    except jwt.InvalidSignatureError as e:
        raise HTTPException(401, "Falhou a verificação da assinatura do token.")
    except jwt.DecodeError as e:
        raise HTTPException(401, "Token inválido ou malformado.")
    except jwt.PyJWTError as e:
        raise HTTPException(401, "Erro ao validar o token.")
