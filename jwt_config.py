from jwt import encode, decode

def dame_token(dato:dict) ->str:
    token:str = encode(payload=dato,key="clavesecreta",algorithm="HS256")
    return token

def validar_token(token:str)->dict:
    dato:dict = decode(token, key="clavesecreta",algorithms=["HS256"])
    return dato