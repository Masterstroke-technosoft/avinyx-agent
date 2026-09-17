from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.agents import AgentTask
from app.models.cases import Case
from app.schemas.agent_tasks import AgentTaskResponse, AgentTaskResult

router = APIRouter()

@router.get("/pending", response_model=List[AgentTaskResponse])
def get_pending_tasks(agent_type: str = None, db: Session = Depends(get_db)):
    """
    Endpoint for Sub-Agents to poll for new tasks.
    Example: GET /api/v1/agent-tasks/pending?agent_type=vision
    """
    query = db.query(AgentTask).filter(AgentTask.status == "pending")
    if agent_type:
        query = query.filter(AgentTask.agent_type == agent_type)
        
    return query.all()

@router.post("/{task_id}/result", response_model=AgentTaskResponse)
def submit_agent_result(task_id: UUID, result_in: AgentTaskResult, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Webhook for Sub-Agents to post their findings.
    This also acts as the Orchestrator by updating the parent Case status.
    """
    task = db.query(AgentTask).filter(AgentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # 1. Update the Agent Task with the result
    task.status = result_in.status # e.g. "completed", "failed"
    task.result_data = result_in.result_data
    db.commit()
    db.refresh(task)
    
    # 2. ORCHESTRATOR LOGIC: Check if all tasks for this case are completed
    all_tasks = db.query(AgentTask).filter(AgentTask.case_id == task.case_id).all()
    if all(t.status == "completed" for t in all_tasks):
        import openai
        import os
        import json
        
        aggregated_findings = {}
        for t in all_tasks:
            aggregated_findings[t.agent_type] = t.result_data
            
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                client = openai.OpenAI(api_key=api_key)
                prompt = f"""
                You are the Master Orchestrator for a Civic System.
                Analyze the following findings from the specialized sub-agents:
                {json.dumps(aggregated_findings, indent=2)}
                
                Based on these combined findings, determine:
                1. master_severity (1-10)
                2. recommended_action (string)
                3. final_intent (string)
                4. assigned_department (string) - MUST be one of: ['Department of Transportation', 'Sanitation', 'Public Works', 'Police', 'Fire Department', 'Parks & Recreation', 'Water Department']
                
                Return ONLY a JSON object with keys: master_severity, recommended_action, final_intent, assigned_department.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                ai_output = json.loads(response.choices[0].message.content)
                
                master_severity = ai_output.get("master_severity", 0)
                final_intent = ai_output.get("final_intent", "unknown")
                assigned_department = ai_output.get("assigned_department", None)
                
                parent_case = db.query(Case).filter(Case.id == task.case_id).first()
                if parent_case:
                    parent_case.ai_severity = master_severity
                    parent_case.ai_intent = final_intent
                    parent_case.assigned_department = assigned_department
                    parent_case.priority = master_severity
                    
                    if master_severity > 5:
                        parent_case.status = "requires_dispatch"
                    else:
                        parent_case.status = "in_progress"
                        
                    db.commit()
                    
                    from app.api.v1.websockets import manager
                    msg = {
                        "case_id": str(parent_case.id), 
                        "status": parent_case.status, 
                        "master_severity": master_severity, 
                        "intent": final_intent,
                        "assigned_department": assigned_department
                    }
                    background_tasks.add_task(manager.broadcast, msg)
            except Exception as e:
                print(f"Orchestrator OpenAI failed: {e}")
    return task
