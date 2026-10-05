from pathlib import Path

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine
from .history_api import router as history_router
from .models import EarthquakeEvent
from .schemas import EarthquakeOut

app = FastAPI(title="Multi-Source State & Reconciliation Platform", version="0.2.0")
app.include_router(history_router)
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/events", response_model=list[EarthquakeOut])
def events(
    limit: int = Query(default=50, ge=1, le=500),
    min_magnitude: float | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(EarthquakeEvent)
    if min_magnitude is not None:
        stmt = stmt.where(EarthquakeEvent.magnitude >= min_magnitude)
    stmt = stmt.order_by(desc(EarthquakeEvent.occurred_at)).limit(limit)
    return list(db.scalars(stmt))


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    stmt = select(EarthquakeEvent).order_by(desc(EarthquakeEvent.occurred_at)).limit(100)
    rows = list(db.scalars(stmt))
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"events": rows},
    )
