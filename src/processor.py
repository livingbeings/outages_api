from .models import OutageRecord, OutageEvent
from .database import get_database
from fastapi import Response,status
import logging

TOLERANCE_MINUTES = 12

async def process_record(record: OutageRecord,response:Response):
    """
    Processing record and write it to db

    Args: 
        record(OutageRecord): json format of outage record
        response(Response): fastapi response
    Return:
        message : json format of message for restful user
    """
    logging.info(f"Processing {record.model_dump_json()}")
    db = get_database()
    collection = db.outage_events
    record.timestamp=record.timestamp.replace(tzinfo=None)

    last_event_doc = await collection.find_one(
        filter={
            "controller_id": record.controller_id,
            "outage_type": record.outage_type.value
        },
        sort=[("end_time", -1)]
    )

    if last_event_doc:
        last_end = last_event_doc["end_time"]
        diff = record.timestamp - last_end
        diff_seconds = diff.total_seconds()

        if 0 < diff_seconds <= TOLERANCE_MINUTES * 60:
            await collection.update_one(
                {"_id": last_event_doc["_id"]},
                {"$set": {"end_time": record.timestamp}}
            )
            return {"message": f"Updated {record.model_dump_json()}"}
        
        if diff_seconds < 0:
            response.status_code=status.HTTP_409_CONFLICT
            return {"message": f"Receiving older record : {record.model_dump_json()}, last record : {last_end}"}

        if diff_seconds == 0:
            response.status_code=status.HTTP_409_CONFLICT
            return {"message": f"Receiving duplicated record : {record.model_dump_json()}, last record : {last_end}"}

    new_event = OutageEvent(
        controller_id=record.controller_id,
        outage_type=record.outage_type,
        start_time=record.timestamp,
        end_time=record.timestamp
    )
    
    event_dict = new_event.model_dump(by_alias=True, exclude={"id"})
    await collection.insert_one(event_dict)
    return {"message": f"Processed {record.model_dump_json()}"}
