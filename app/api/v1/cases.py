import os
import shutil
import math
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
import json
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.cases import Case, MediaAttachment
from app.models.users import User
from app.schemas.cases import CaseCreate, CaseResponse, MediaResponse
from app.api.deps import get_current_user, RequirePermissions

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # radius of earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.post("/", response_model=CaseResponse, name="File a Complaint")
def create_case(
    case_data: str = Form(..., description="JSON string containing CaseCreate data"), 
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a new civic complaint ticket with optional photo/video evidence in one step."""
    
    try:
        parsed_data = json.loads(case_data)
        case_in = CaseCreate(**parsed_data)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON data in case_data: {e}")
        
    new_case = Case(
        citizen_id=current_user.id,
        title=case_in.title,
        description=case_in.description,
        latitude=case_in.latitude,
        longitude=case_in.longitude,
        ward=case_in.ward,
        priority=case_in.priority
    )
    
    # Phase 5: Geo-Spatial Deduplication
    is_duplicate = False
    if case_in.latitude is not None and case_in.longitude is not None:
        recent_cases = db.query(Case).filter(Case.status != "closed", Case.latitude.isnot(None), Case.longitude.isnot(None)).all()
        for c in recent_cases:
            dist = haversine(case_in.latitude, case_in.longitude, c.latitude, c.longitude)
            if dist <= 50: # within 50 meters
                is_duplicate = True
                new_case.status = "duplicate"
                break

    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    if is_duplicate:
        return new_case
        
    # ORCHESTRATOR TRIGGER: Spawn a task for the Text Agent
    from app.models.agents import AgentTask
    from app.core.queue import publish_task
    
    text_payload = {"description": new_case.description, "title": new_case.title}
    text_task = AgentTask(
        case_id=new_case.id,
        agent_type="text",
        status="pending",
        payload=text_payload
    )
    db.add(text_task)
    db.commit()
    db.refresh(text_task)
    
    queue_payload = {
        "task_id": str(text_task.id),
        "case_id": str(new_case.id),
        "agent_type": "text",
        "payload": text_payload
    }
    publish_task("text_queue", queue_payload)
    
    # ORCHESTRATOR TRIGGER: Spawn a task for the Geo Agent
    geo_payload = {"latitude": new_case.latitude, "longitude": new_case.longitude, "ward": new_case.ward}
    geo_task = AgentTask(
        case_id=new_case.id,
        agent_type="geo",
        status="pending",
        payload=geo_payload
    )
    db.add(geo_task)
    db.commit()
    
    geo_queue_payload = {
        "task_id": str(geo_task.id),
        "case_id": str(new_case.id),
        "agent_type": "geo",
        "payload": geo_payload
    }
    publish_task("geo_queue", geo_queue_payload)
    
    # NEW: Handle File Upload & Vision Agent
    if file:
        if file.content_type not in ["image/jpeg", "image/png", "video/mp4"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, and MP4 allowed.")
            
        file_location = f"{UPLOAD_DIR}/{new_case.id}_{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
            
        attachment = MediaAttachment(
            case_id=new_case.id,
            file_url=file_location,
            media_type="image" if "image" in file.content_type else "video",
            stage="before"
        )
        db.add(attachment)
        
        vision_payload = {"file_url": file_location, "media_type": attachment.media_type}
        vision_task = AgentTask(
            case_id=new_case.id,
            agent_type="vision",
            status="pending",
            payload=vision_payload
        )
        db.add(vision_task)
        db.commit()
        
        vision_queue_payload = {
            "task_id": str(vision_task.id),
            "case_id": str(new_case.id),
            "agent_type": "vision",
            "payload": vision_payload
        }
        publish_task("vision_queue", vision_queue_payload)
    
    return new_case

@router.get("/me", response_model=List[CaseResponse])
def get_my_cases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all tickets submitted by the logged-in user."""
    cases = db.query(Case).filter(Case.citizen_id == current_user.id).all()
    return cases

@router.get("/", response_model=List[CaseResponse])
def get_all_cases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Admin and Department endpoint to list tickets."""
    has_read_all = any(perm.name == "cases:read_all" for role in current_user.roles for perm in role.permissions)
    has_read_dept = any(perm.name == "cases:read_department" for role in current_user.roles for perm in role.permissions)
    
    if has_read_all:
        return db.query(Case).all()
    elif has_read_dept and current_user.department_name:
        return db.query(Case).filter(Case.assigned_department == current_user.department_name).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view all cases")

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get details of a specific ticket."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Security: Only Admins, Department users for their dept, or ticket owner can view it
    if case.citizen_id != current_user.id:
        has_admin_perm = any(perm.name == "cases:read_all" for role in current_user.roles for perm in role.permissions)
        has_dept_perm = any(perm.name == "cases:read_department" for role in current_user.roles for perm in role.permissions)
        if has_admin_perm:
            pass
        elif has_dept_perm and case.assigned_department == current_user.department_name:
            pass
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view this case")
            
    return case

@router.get("/{case_id}/analysis")
def get_case_analysis(case_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve the deep AI analysis (Vision, Text, Geo) for a specific ticket."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Security check
    if case.citizen_id != current_user.id:
        has_admin_perm = any(perm.name == "cases:read_all" for role in current_user.roles for perm in role.permissions)
        has_dept_perm = any(perm.name == "cases:read_department" for role in current_user.roles for perm in role.permissions)
        if has_admin_perm:
            pass
        elif has_dept_perm and case.assigned_department == current_user.department_name:
            pass
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view analysis for this case")
            
    from app.models.agents import AgentTask
    from app.schemas.agent_tasks import AgentTaskResponse
    
    tasks = db.query(AgentTask).filter(AgentTask.case_id == case_id).all()
    
    # We return a clean dictionary summarizing the AI's findings
    analysis_report = {
        "case_id": case.id,
        "current_status": case.status,
        "ai_tasks": []
    }
    
    for task in tasks:
        analysis_report["ai_tasks"].append({
            "task_id": task.id,
            "agent_type": task.agent_type,
            "status": task.status,
            "findings": task.result_data
        })
        
    return analysis_report
