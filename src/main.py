from fastapi import FastAPI, Query, HTTPException, APIRouter,Response
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from .database import db, get_database
from .models import OutageRecord, OutageEvent, OutageType
from .processor import process_record

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()
    yield
    db.close()

app = FastAPI(title="Outage API", lifespan=lifespan)
router = APIRouter(prefix="/api/v1")

@router.post("/outages", status_code=202)
async def report_outages(record: OutageRecord,response:Response):
    """
    Ingest outage records. 
    Accepts a list of records. 
    Records are processed to aggregate consecutive outages into events.
    """
    return await process_record(record,response)
    

@router.get("/events", response_model=List[OutageEvent])
async def get_events(
    controller_id: Optional[str] = None,
    outage_type: Optional[OutageType] = None,
    start_time: Optional[datetime] = Query(None, description="Filter events starting at or after this time"),
    end_time: Optional[datetime] = Query(None, description="Filter events ending at or before this time"),
    limit: int = 100,
    skip: int = 0
):
    """
    Query grouped outage events.
    """
    query = {}
    if controller_id:
        query["controller_id"] = controller_id
    if outage_type:
        query["outage_type"] = outage_type.value
    
    if start_time:
        query["start_time"] = {"$gte": start_time}
    if end_time:
        query["end_time"] = {"$lte": end_time}

    db_instance = get_database()
    cursor = db_instance.outage_events.find(query).skip(skip).limit(limit)
    
    events = []
    async for doc in cursor:
        # Convert ObjectId to string
        doc["_id"] = str(doc["_id"])
        events.append(doc)
        
    return events

@app.get("/")
def read_root():
    return {"message": "Outages API. Go to /docs for Swagger UI."}

app.include_router(router=router)
