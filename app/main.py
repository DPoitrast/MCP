import logging # Added
from fastapi import Depends, FastAPI, HTTPException, status, Request # Added Request
from fastapi.security import OAuth2PasswordBearer

from . import crud, models, schemas
from .database import get_db, init_db

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    # handlers=[logging.StreamHandler()] # Not strictly necessary, stdout is default
)

init_db()

app = FastAPI(title="MCP Server PoC")

# Middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.get("/healthz", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    Returns a 200 status if the server is healthy.
    """
    return {"status": "healthy"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dummy token check for example purposes
async def get_current_token(token: str = Depends(oauth2_scheme)):
    if token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logging.warning("Successful authentication using a dummy token. Replace in production.") # Added illustrative log
    return token


@app.get("/api/v1/herd", response_model=list[schemas.Herd])
async def list_herd(skip: int = 0, limit: int = 100, token: str = Depends(get_current_token)):
    with get_db() as db:
        herds = crud.get_herd(db, skip=skip, limit=limit)
    return herds


@app.post("/api/v1/herd", response_model=schemas.Herd, status_code=status.HTTP_201_CREATED)
async def create_new_herd(herd_data: schemas.HerdCreate, token: str = Depends(get_current_token)):
    """
    Create a new herd.
    """
    with get_db() as db:
        created_herd = crud.create_herd(db=db, herd=herd_data)
    return created_herd
