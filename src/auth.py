from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader


api_key_header = APIKeyHeader(name='A-API-Key', auto_error=False)

def verify_api_key(api_key: str=Security(api_key_header)):
    if api_key != "STATIKEY":
        raise  HTTPException(status_code=401,detail="Invalid API Key")
    return api_key