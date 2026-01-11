from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Annotated 
from fastapi import Body

class OutageType(str, Enum):
    PANEL_OUTAGE = "panel_outage"
    TEMPERATURE_OUTAGE = "temperature_outage"
    LED_OUTAGE = "led_outage"

class OutageRecord(BaseModel):
    controller_id: str
    outage_type: OutageType
    timestamp: Annotated[datetime, Body()]

class OutageEvent(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    controller_id: str
    outage_type: OutageType
    start_time: Annotated[datetime, Body()]
    end_time: Annotated[datetime, Body()]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "controller_id": "controller_123",
                "outage_type": "panel_outage",
                "start_time": "2023-10-27T10:00:00",
                "end_time": "2023-10-27T12:00:00"
            }
        }

class OutageEventFilter(BaseModel):
    controller_id: Optional[str] = None
    outage_type: Optional[OutageType] = None
    start_time_min: Optional[datetime] = None
    end_time_max: Optional[datetime] = None
