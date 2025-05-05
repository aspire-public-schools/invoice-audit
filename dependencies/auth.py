import os
from fastapi import Header, HTTPException, status

def verify_api_key(x_api_key: str = Header(...)):
    expected = os.getenv("API_KEY")
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
