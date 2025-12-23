"""BFF controller for core entity management."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.auth_models import TokenPayload, UserRole
from app.models.workitem_models import (
    CreateWorkitemRequest, UpdateWorkitemRequest, 
    Workitem, WorkitemType
)
from app.models.testcase_models import (
    CreateTestcaseRequest, UpdateTestcaseRequest, Testcase
)
from app.models.testsuite_models import (
    CreateTestsuiteRequest, UpdateTestsuiteRequest, Testsuite
)
from app.services.workitem_service import WorkitemService
from app.services.testcase_service import TestcaseService
from app.services.testsuite_service import TestsuiteService
from app.services.execution_service import ExecutionService
from app.services.user_service import UserService
from app.models.common_models import Environment
from app.database import get_database
from app.middleware.rbac import get_current_user, require_org_member, require_org_admin

router = APIRouter(prefix="/testaurant/v1/bff", tags=["BFF"])


# --- Workitems ---

@router.post("/workitems", response_model=Workitem)
async def create_workitem(
    request: CreateWorkitemRequest,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Create a new workitem."""
    return await WorkitemService.create_workitem(
        current_user.organization_id,
        request.model_dump(),
        current_user.user_id
    )

@router.get("/workitems")
async def list_workitems(
    workitem_type: Optional[WorkitemType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(require_org_member)
):
    """List workitems."""
    items = await WorkitemService.list_workitems(
        current_user.organization_id,
        workitem_type,
        skip,
        limit
    )
    
    # Resolve user names
    user_ids = []
    for item in items:
        if item.created_by: user_ids.append(item.created_by)
        if item.last_ran_by: user_ids.append(item.last_ran_by)
    
    user_map = await UserService.resolve_user_names(user_ids)
    
    enriched_items = []
    for item in items:
        # Dump to dict using aliases
        item_dict = item.model_dump(by_alias=True)
        # Add the resolved names
        item_dict["created_by_name"] = user_map.get(item.created_by, item.created_by)
        item_dict["last_ran_by_name"] = user_map.get(item.last_ran_by, item.last_ran_by)
        enriched_items.append(item_dict)
        
    return enriched_items

@router.get("/workitems/{workitem_id}", response_model=Workitem)
async def get_workitem(
    workitem_id: str,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Get workitem by ID."""
    workitem = await WorkitemService.get_workitem(
        workitem_id, 
        current_user.organization_id
    )
    if not workitem:
        raise HTTPException(status_code=404, detail="Workitem not found")
    return workitem

@router.put("/workitems/{workitem_id}", response_model=Workitem)
async def update_workitem(
    workitem_id: str,
    request: UpdateWorkitemRequest,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Update a workitem."""
    return await WorkitemService.update_workitem(
        workitem_id,
        current_user.organization_id,
        request.model_dump(exclude_unset=True),
        current_user.user_id
    )

@router.delete("/workitems/{workitem_id}")
async def delete_workitem(
    workitem_id: str,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Delete a workitem."""
    success = await WorkitemService.delete_workitem(
        workitem_id,
        current_user.organization_id,
        current_user.user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Workitem not found")
    return {"message": "Workitem deleted successfully"}


# --- Testcases ---

@router.post("/testcases", response_model=Testcase)
async def create_testcase(
    request: CreateTestcaseRequest,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Create a new testcase."""
    return await TestcaseService.create_testcase(
        current_user.organization_id,
        request.model_dump(),
        current_user.user_id
    )

@router.get("/testcases")
async def list_testcases(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(require_org_member)
):
    """List testcases."""
    items = await TestcaseService.list_testcases(
        current_user.organization_id,
        skip,
        limit
    )
    
    # Resolve user names
    user_ids = []
    for item in items:
        if item.created_by: user_ids.append(item.created_by)
        if item.last_ran_by: user_ids.append(item.last_ran_by)
        
    user_map = await UserService.resolve_user_names(user_ids)
    
    enriched_items = []
    for item in items:
        item_dict = item.model_dump(by_alias=True)
        item_dict["created_by_name"] = user_map.get(item.created_by, item.created_by)
        item_dict["last_ran_by_name"] = user_map.get(item.last_ran_by, item.last_ran_by)
        enriched_items.append(item_dict)
        
    return enriched_items

@router.get("/testcases/{testcase_id}", response_model=Testcase)
async def get_testcase(
    testcase_id: str,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Get testcase by ID."""
    testcase = await TestcaseService.get_testcase(
        testcase_id, 
        current_user.organization_id
    )
    if not testcase:
        raise HTTPException(status_code=404, detail="Testcase not found")
    return testcase

@router.put("/testcases/{testcase_id}", response_model=Testcase)
async def update_testcase(
    testcase_id: str,
    request: UpdateTestcaseRequest,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Update a testcase."""
    return await TestcaseService.update_testcase(
        testcase_id,
        current_user.organization_id,
        request.model_dump(exclude_unset=True),
        current_user.user_id
    )

@router.delete("/testcases/{testcase_id}")
async def delete_testcase(
    testcase_id: str,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Delete a testcase."""
    success = await TestcaseService.delete_testcase(
        testcase_id,
        current_user.organization_id,
        current_user.user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Testcase not found")
    return {"message": "Testcase deleted successfully"}


# --- Testsuites ---

@router.post("/testsuites", response_model=Testsuite)
async def create_testsuite(
    request: CreateTestsuiteRequest,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Create a new testsuite."""
    return await TestsuiteService.create_testsuite(
        current_user.organization_id,
        request.model_dump(),
        current_user.user_id
    )

@router.get("/testsuites")
async def list_testsuites(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(require_org_member)
):
    """List testsuites."""
    items = await TestsuiteService.list_testsuites(
        current_user.organization_id,
        skip,
        limit
    )
    
    # Resolve user names
    user_ids = []
    for item in items:
        if item.created_by: user_ids.append(item.created_by)
        if item.last_ran_by: user_ids.append(item.last_ran_by)
        
    user_map = await UserService.resolve_user_names(user_ids)
    
    enriched_items = []
    for item in items:
        item_dict = item.model_dump(by_alias=True)
        item_dict["created_by_name"] = user_map.get(item.created_by, item.created_by)
        item_dict["last_ran_by_name"] = user_map.get(item.last_ran_by, item.last_ran_by)
        enriched_items.append(item_dict)
        
    return enriched_items

@router.get("/testsuites/{testsuite_id}", response_model=Testsuite)
async def get_testsuite(
    testsuite_id: str,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Get testsuite by ID."""
    testsuite = await TestsuiteService.get_testsuite(
        testsuite_id, 
        current_user.organization_id
    )
    if not testsuite:
        raise HTTPException(status_code=404, detail="Testsuite not found")
    return testsuite

@router.put("/testsuites/{testsuite_id}", response_model=Testsuite)
async def update_testsuite(
    testsuite_id: str,
    request: UpdateTestsuiteRequest,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Update a testsuite."""
    return await TestsuiteService.update_testsuite(
        testsuite_id,
        current_user.organization_id,
        request.model_dump(exclude_unset=True),
        current_user.user_id
    )

@router.delete("/testsuites/{testsuite_id}")
async def delete_testsuite(
    testsuite_id: str,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Delete a testsuite."""
    success = await TestsuiteService.delete_testsuite(
        testsuite_id,
        current_user.organization_id,
        current_user.user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Testsuite not found")
    return {"message": "Testsuite deleted successfully"}


# --- Statistics ---

@router.get("/stats")
async def get_stats(
    current_user: TokenPayload = Depends(require_org_member)
):
    """Get counts for dashboard stats."""
    db = get_database()
    workitem_count = await WorkitemService.count_workitems(current_user.organization_id)
    testcase_count = await TestcaseService.count_testcases(current_user.organization_id)
    testsuite_count = await TestsuiteService.count_testsuites(current_user.organization_id)
    execution_count = await db.run_workitem_audit.count_documents({"organization_id": current_user.organization_id})
    
    return {
        "workitems": workitem_count,
        "testcases": testcase_count,
        "testsuites": testsuite_count,
        "executions": execution_count
    }


# --- Executions ---

@router.get("/executions")
async def list_all_executions(
    current_user: TokenPayload = Depends(require_org_member)
):
    """List all recent executions across all types."""
    db = get_database()
    
    # 1. Fetch from all collections
    wi_runs = await db.run_workitem_audit.find({"organization_id": current_user.organization_id}).sort("run_workitem_created_date", -1).limit(50).to_list(50)
    tc_runs = await db.run_testcase_audit.find({"organization_id": current_user.organization_id}).sort("run_testcase_created_date", -1).limit(50).to_list(50)
    ts_runs = await db.run_testsuite_audit.find({"organization_id": current_user.organization_id}).sort("run_testsuite_created_date", -1).limit(50).to_list(50)
    
    # 2. Normalize and merge
    unified_runs = []
    
    for r in wi_runs:
        unified_runs.append({
            "id": r["run_workitem_id"],
            "entity_id": r["workitem_id"],
            "name": r["workitem_title"],
            "type": "workitem",
            "status": r["execution_status"],
            "created_at": r["run_workitem_created_date"],
            "executor_context": r.get("executor_context")
        })
        
    for r in tc_runs:
        unified_runs.append({
            "id": r["run_testcase_id"],
            "entity_id": r["testcase_id"],
            "name": r["testcase_title"],
            "type": "testcase",
            "status": r["overall_status"],
            "created_at": r["run_testcase_created_date"],
            "executor_context": r.get("executor_context")
        })

    for r in ts_runs:
        unified_runs.append({
            "id": r["run_testsuite_id"],
            "entity_id": r["testsuite_id"],
            "name": r["testsuite_title"],
            "type": "testsuite",
            "status": r["overall_status"],
            "created_at": r["run_testsuite_created_date"],
            "executor_context": r.get("executor_context")
        })

    # 3. Sort by date descending
    unified_runs.sort(key=lambda x: x["created_at"], reverse=True)
    unified_runs = unified_runs[:50]
    
    # 4. Resolve names
    user_ids = [r.get("executor_context") for r in unified_runs if r.get("executor_context")]
    user_map = await UserService.resolve_user_names(user_ids)
    
    for r in unified_runs:
        uid = r.get("executor_context")
        r["executor_name"] = user_map.get(uid, uid)
        
    return {"runs": unified_runs}

@router.get("/executions/workitem/{run_id}")
async def get_workitem_execution(
    run_id: str,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Get full audit for a workitem run."""
    db = get_database()
    run = await db.run_workitem_audit.find_one({
        "run_workitem_id": run_id,
        "organization_id": current_user.organization_id
    })
    if not run:
        raise HTTPException(status_code=404, detail="Workitem run not found")
    # Convert ObjectId to string
    run["_id"] = str(run["_id"])
    return run

@router.get("/executions/testcase/{run_id}")
async def get_testcase_execution(
    run_id: str,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Get full audit for a testcase run."""
    db = get_database()
    run = await db.run_testcase_audit.find_one({
        "run_testcase_id": run_id,
        "organization_id": current_user.organization_id
    })
    if not run:
        raise HTTPException(status_code=404, detail="Testcase run not found")
    run["_id"] = str(run["_id"])
    return run

@router.get("/executions/testsuite/{run_id}")
async def get_testsuite_execution(
    run_id: str,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Get full audit for a testsuite run."""
    db = get_database()
    run = await db.run_testsuite_audit.find_one({
        "run_testsuite_id": run_id,
        "organization_id": current_user.organization_id
    })
    if not run:
        raise HTTPException(status_code=404, detail="Testsuite run not found")
    run["_id"] = str(run["_id"])
    return run

@router.get("/runnable")
async def list_runnable_entities(
    current_user: TokenPayload = Depends(require_org_member)
):
    """List all runnable items (Workitems, Testcases, Testsuites)."""
    wis = await WorkitemService.list_workitems(current_user.organization_id, limit=100)
    tcs = await TestcaseService.list_testcases(current_user.organization_id, limit=100)
    tss = await TestsuiteService.list_testsuites(current_user.organization_id, limit=100)
    
    # Normalize
    runnables = []
    
    for i in wis:
        runnables.append({
            "id": i.workitem_id,
            "name": i.name,
            "type": "workitem",
            "description": i.description,
            "created_by": i.created_by,
            "created_by_name": i.created_by_name
        })
    
    for i in tcs:
        runnables.append({
            "id": i.testcase_id,
            "name": i.name,
            "type": "testcase",
            "description": i.description,
            "created_by": i.created_by,
            "created_by_name": i.created_by_name
        })
        
    for i in tss:
        runnables.append({
            "id": i.testsuite_id,
            "name": i.name,
            "type": "testsuite",
            "description": i.description,
            "created_by": i.created_by,
            "created_by_name": i.created_by_name
        })
        
    return {"items": runnables}

@router.post("/run/workitem/{workitem_id}")
async def run_workitem(
    workitem_id: str,
    environment: Environment = Environment.QA,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Run a workitem."""
    return await ExecutionService.run_workitem(
        current_user.organization_id,
        workitem_id,
        environment,
        current_user.user_id
    )

@router.post("/run/testcase/{testcase_id}")
async def run_testcase(
    testcase_id: str,
    environment: Environment = Environment.QA,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Run a testcase."""
    return await ExecutionService.run_testcase(
        current_user.organization_id,
        testcase_id,
        environment,
        current_user.user_id
    )

@router.post("/run/testsuite/{testsuite_id}")
async def run_testsuite(
    testsuite_id: str,
    environment: Environment = Environment.QA,
    current_user: TokenPayload = Depends(require_org_member)
):
    """Run a testsuite."""
    return await ExecutionService.run_testsuite(
        current_user.organization_id,
        testsuite_id,
        environment,
        current_user.user_id
    )
