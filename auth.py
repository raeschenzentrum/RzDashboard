# auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import pam  # PAM-Modul für OS-Authentifizierung

router = APIRouter()

# Token model for responses
class Token(BaseModel):
    access_token: str
    token_type: str

# OAuth2 Bearer Token setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funktion zur Überprüfung des Betriebssystem-Logins
def authenticate_os_user(username: str, password: str) -> bool:
    pam_auth = pam.pam()
    return pam_auth.authenticate(username, password)

# Endpoint to provide authentication token using OS login
@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_os_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": form_data.username, "token_type": "bearer"}

# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token  # Return the token (username in this case)
