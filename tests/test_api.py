import pytest
from httpx import AsyncClient, ASGITransport
from ..src.main import app
from ..src.database import db
from ..src.models import OutageType
from datetime import datetime, timedelta
import os

# SKIP tests if no mongo connection (optional check)
# But for now we assume environment is set up.

@pytest.fixture(autouse=True)
def setup_database():
    db.connect()
    yield
    db.close()

@pytest.mark.asyncio
async def test_flow():
    # Use ASGITransport for direct app testing
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # Clean up or use unique IDs in real tests
        cid = f"test_ctrl_{datetime.now().timestamp()}"
        
        # 1. Start an outage
        t1 = datetime(2023, 1, 1, 10, 0, 0)
        res = await ac.post("/api/v1/outages", json=
            {
                "controller_id": cid,
                "outage_type": "panel_outage",
                "timestamp": t1.isoformat()
            }
        )
        assert res.status_code == 202
        
        # 2. Extend it (10 mins later)
        t2 = t1 + timedelta(minutes=10)
        res = await ac.post("/api/v1/outages", json=
            {
                "controller_id": cid,
                "outage_type": "panel_outage",
                "timestamp": t2.isoformat()
            }
        )
        assert res.status_code == 202
        
        # 3. Extend it again (another 10 mins)
        t3 = t2 + timedelta(minutes=10)
        res = await ac.post("/api/v1/outages", json=
            {
                "controller_id": cid,
                "outage_type": "panel_outage",
                "timestamp": t3.isoformat()
            }
        )
        assert res.status_code == 202
        
        # 4. Create a gap (30 mins later than t3) -> New Event
        t4 = t3 + timedelta(minutes=30)
        res = await ac.post("/api/v1/outages", json=
            {
                "controller_id": cid,
                "outage_type": "panel_outage",
                "timestamp": t4.isoformat()
            }
        )
        assert res.status_code == 202
        
        # 5. Query
        res = await ac.get("/api/v1/events", params={"controller_id": cid})
        assert res.status_code == 200
        events = res.json()
        
        # We expect 2 events
        # Event 1: t1 to t3
        # Event 2: t4 to t4
        
        # Sort by start_time to be sure
        events.sort(key=lambda x: x["start_time"])
        
        assert len(events) == 2
        
        e1 = events[0]
        assert e1["start_time"] == t1.isoformat()
        assert e1["end_time"] == t3.isoformat()
        
        e2 = events[1]
        assert e2["start_time"] == t4.isoformat()
        assert e2["end_time"] == t4.isoformat()

