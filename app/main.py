import json
import logging
from time import perf_counter

from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from . import models, crud, schemas
from .database import engine, get_db

# Screencast Demo: This change triggers a new Render deployment NEW
# Test
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="C3-Template-App")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key in ("method", "path", "status_code", "duration_ms", "item_id", "count"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("c3.app")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    duration_ms = round((perf_counter() - start_time) * 1000, 2)
    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.on_event("startup")
def on_startup():
    logger.info("application_startup")


@app.get("/", tags=["root"])
def read_root():
    # Screencast deployment test version 2
    logger.info("root_requested")
    return {"status": "ok", "service": "C3-Template-App"}


@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    created_item = crud.create_item(db, item)
    logger.info("item_created", extra={"item_id": created_item.id})
    return created_item


@app.get("/items/", response_model=list[schemas.Item])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.list_items(db, skip=skip, limit=limit)
    logger.info("items_listed", extra={"count": len(items)})
    return items


@app.get("/items/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        logger.info("item_not_found", extra={"item_id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info("item_read", extra={"item_id": item_id})
    return db_item
