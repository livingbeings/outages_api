# Outage API

## Overview

This project implements a backend service to aggregate continuous outage reports from LED controllers into grouped outage events. It provides a RESTful API to ingest outage records and query aggregated events.

## Architecture

- **Framework**: FastAPI (Python)
- **Database**: MongoDB (accessed via Motor for async support)
- **Data Processing**:
    - Incoming outage records are processed to either extend an existing outage event or create a new one.
    - Logic handles consecutive reports (every 10 minutes) by checking if the new record falls within a tolerance window (12 minutes) of the previous event's end time.

## Design Decisions

1. **Aggregation Logic**:
   - The system queries the most recent event for a given `controller_id` and `outage_type`.
   - If the new record's timestamp is within 12 minutes of the last event's `end_time`, the event is extended.
   - This handles the "10-minute reporting" requirement with a slight buffer for network delays.
   - This approach allows for real-time processing as records arrive.

2. **Database**:
   - MongoDB was chosen for its flexibility and ease of use with JSON-like data.
   - Using `motor` allows non-blocking database operations, essential for a high-performance FastAPI application.

3. **API Structure**:
   - `POST /outages`: Accepts a single outage record.
   - `GET /events`: Supports filtering by controller, type, and time range.

## Documentation

A sequence diagram describing the system flow is available in `docs/diagram.puml`.

## Setup Instructions

### Local Setup

1. **Prerequisites**: Python 3.9+, MongoDB running locally.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables**:
   Create a `.env` file (optional, defaults provided):
   ```
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=outages_db
   ```
4. **Run Application**:
   ```bash
   uvicorn src.main:app --reload
   ```
   Access API docs at `http://localhost:8000/docs`.

### Docker Setup

1. Build image:
   ```bash
   docker compose -f docker/compose.yaml build
   ```
2. Run container (ensure MongoDB is accessible, e.g., via host networking or docker-compose):
   ```bash
   docker compose -f docker/compose.yaml up -d
   ```

### Docker Compose Setup (Recommended)

Run the entire stack (App + MongoDB) with a single command:

```bash
docker compose up --build
```

## API Usage Examples

**Ingest Outages:**
```json
POST /outages
{
  "controller_id": "ctrl_1",
  "outage_type": "panel_outage",
  "timestamp": "2023-10-27T10:00:00"
}
```

**Query Events:**
```
GET /events?controller_id=ctrl_1&start_time=2023-10-27T00:00:00
```

## To Do List
1. **GCP Deployment with Git Action**  
Git action could be configured to upload to gcp artifact on receiving any git tag or and push to master. Then Cloud Run or App Engine can auto load newer image based on latest version in artifact
2. **Assumption Handling**   
At this state, the controller is assumed to only upload latest record. However, it is still possible for the controller to upload older record and it still needed to be handled to properly store a complete historical data of outage event.