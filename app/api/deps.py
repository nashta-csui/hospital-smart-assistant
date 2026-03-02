from fastapi import Header, HTTPException
from typing import Optional
from app.repositories.in_memory_repository import InMemoryPasienRepository
from app.repositories.interfaces import IPasienRepository

global_repo = InMemoryPasienRepository()

def get_repo() -> IPasienRepository:
    return global_repo

def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    if not token.startswith("user-"):
        raise HTTPException(status_code=401, detail="Invalid token")
        
    return token.replace("user-", "")
