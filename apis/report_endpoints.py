from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from utils.report_generator import generate_report, reports
import uuid
import os

router = APIRouter()

@router.post("/trigger_report")
def trigger_report(background_tasks: BackgroundTasks):
    report_id = str(uuid.uuid4())
    reports[report_id] = "Running"
    background_tasks.add_task(generate_report, report_id)
    return {"report_id": report_id}

@router.get("/get_report")
def get_report(report_id: str):
    status = reports.get(report_id)
    if not status:
        raise HTTPException(status_code=404, detail="Report not found")
    if status == "Running":
        return {"status": "Running"}

    file_path = status
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Report file missing")

    return FileResponse(
        path=file_path,
        media_type='text/csv',
        filename=os.path.basename(file_path)
    )
