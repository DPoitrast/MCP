from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from . import crud, models, schemas
from .database import get_db, init_db

init_db()

app = FastAPI(title="MCP Server PoC")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dummy token check for example purposes
async def get_current_token(token: str = Depends(oauth2_scheme)):
    if token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@app.get("/api/v1/herd", response_model=list[schemas.Herd])
async def list_herd(skip: int = 0, limit: int = 100, token: str = Depends(get_current_token)):
    with get_db() as db:
        herds = crud.get_herd(db, skip=skip, limit=limit)
    return herds
