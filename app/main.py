import logging
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from . import crud, models, schemas
from .database import get_db, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

app = FastAPI(title="MCP Server PoC")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_id": str(id(exc))}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

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


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring service status."""
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/v1/herd", response_model=list[schemas.Herd])
async def list_herd(skip: int = 0, limit: int = 100, token: str = Depends(get_current_token)):
    """List herds with pagination support."""
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip must be non-negative")
    if limit <= 0 or limit > 1000:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
    
    try:
        with get_db() as db:
            herds = crud.get_herd(db, skip=skip, limit=limit)
        logger.info(f"Listed {len(herds)} herds (skip={skip}, limit={limit})")
        return herds
    except Exception as e:
        logger.error(f"Failed to list herds: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve herds")


@app.get("/api/v1/herd/{herd_id}", response_model=schemas.Herd)
async def get_herd(herd_id: int, token: str = Depends(get_current_token)):
    """Get a specific herd by ID."""
    if herd_id <= 0:
        raise HTTPException(status_code=400, detail="Herd ID must be positive")
    
    try:
        with get_db() as db:
            herd = crud.get_herd_by_id(db, herd_id)
        if not herd:
            raise HTTPException(status_code=404, detail="Herd not found")
        logger.info(f"Retrieved herd {herd_id}")
        return herd
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get herd {herd_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve herd")


@app.post("/api/v1/herd", response_model=schemas.Herd, status_code=201)
async def create_herd(herd: schemas.HerdCreate, token: str = Depends(get_current_token)):
    """Create a new herd."""
    try:
        with get_db() as db:
            new_herd = crud.create_herd(db, herd)
        logger.info(f"Created herd {new_herd.id}: {new_herd.name}")
        return new_herd
    except Exception as e:
        logger.error(f"Failed to create herd: {e}")
        raise HTTPException(status_code=500, detail="Failed to create herd")


@app.delete("/api/v1/herd/{herd_id}", status_code=204)
async def delete_herd(herd_id: int, token: str = Depends(get_current_token)):
    """Delete a herd by ID."""
    if herd_id <= 0:
        raise HTTPException(status_code=400, detail="Herd ID must be positive")
    
    try:
        with get_db() as db:
            deleted = crud.delete_herd(db, herd_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Herd not found")
        logger.info(f"Deleted herd {herd_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete herd {herd_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete herd")
