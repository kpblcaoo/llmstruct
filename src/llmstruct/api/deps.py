from fastapi import Header, HTTPException

API_KEY = "dev-key"

async def get_api_key(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid API key")
    token = authorization.split(" ", 1)[1]
    if token != API_KEY:
        raise HTTPException(403, "Invalid API key")
    return token 