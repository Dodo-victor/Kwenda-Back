from fastapi import Depends, HTTPException, status, Header
from core.utilis.security import get_algorithm
from core.utilis.generate_token import verifield_token 
from core.utilis.messages import Messages

def organization_middleware(x_auth_token: str = Header(...)) -> dict | None:

    validte_token =  verifield_token(x_auth_token)
    print("token01",validte_token)
    if validte_token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.token_invalid)

    if isinstance(validte_token, dict):
        print("token02",validte_token)
        return validte_token
    
    