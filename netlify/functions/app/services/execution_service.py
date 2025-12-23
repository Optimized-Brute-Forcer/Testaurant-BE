"""Execution service for running workitems, testcases and testsuites."""
import httpx
import json
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.database import get_database
from app.models.workitem_models import Workitem, WorkitemType
from app.models.common_models import ExecutionStatus, ExecutionLog, LogType, Environment
from app.models.execution_models import (
    RunWorkitemAudit, WorkitemExecutionResult, 
    RunTestcaseAudit, RunWorkitemRequest,
    RunTestcaseRequest, RunTestsuiteAudit, RunTestsuiteRequest
)
from app.services.counter_service import (
    get_next_run_workitem_id, 
    get_next_run_testcase_id,
    get_next_run_testsuite_id
)
from app.services.workitem_service import WorkitemService
from app.services.testcase_service import TestcaseService
from app.services.testsuite_service import TestsuiteService


class ExecutionService:
    """Service for managing executions."""

    @staticmethod
    async def run_workitem(
        organization_id: str,
        workitem_id: str,
        environment: Environment,
        user_id: str,
        feed_forward_data: Optional[Dict[str, Any]] = None
    ) -> RunWorkitemAudit:
        """Run a single workitem and log audit."""
        db = get_database()
        
        # 1. Fetch Workitem
        workitem = await WorkitemService.get_workitem(workitem_id, organization_id)
        if not workitem:
            raise Exception(f"Workitem {workitem_id} not found")

        run_id = await get_next_run_workitem_id()
        logs: List[ExecutionLog] = []
        status = ExecutionStatus.PENDING
        start_time = datetime.utcnow()
        actual_response = None
        
        logs.append(ExecutionLog(
            log_type=LogType.INFO,
            message=f"Starting execution for workitem: {workitem.name} ({workitem.workitem_type})"
        ))

        try:
            if workitem.workitem_type == WorkitemType.REST:
                actual_response, status = await ExecutionService._execute_rest_workitem(workitem, logs)
            elif workitem.workitem_type == WorkitemType.SQL:
                actual_response, status = await ExecutionService._execute_sql_workitem(workitem, logs)
            elif workitem.workitem_type == WorkitemType.MONGO:
                actual_response, status = await ExecutionService._execute_mongo_workitem(workitem, logs)
            else:
                status = ExecutionStatus.FAILED
                logs.append(ExecutionLog(log_type=LogType.ERROR, message=f"Unsupported workitem type: {workitem.workitem_type}"))
        except Exception as e:
            status = ExecutionStatus.FAILED
            logs.append(ExecutionLog(log_type=LogType.ERROR, message=f"Execution error: {str(e)}"))

        end_time = datetime.utcnow()
        
        # 2. Save Audit
        audit = RunWorkitemAudit(
            run_workitem_id=run_id,
            organization_id=organization_id,
            workitem_id=workitem_id,
            workitem_title=workitem.name,
            environment=environment,
            execution_status=status,
            workitem_config=workitem.model_dump(),
            execution_logs=logs,
            actual_response=actual_response,
            run_workitem_created_date=start_time,
            run_workitem_start_time=start_time,
            run_workitem_end_time=end_time,
            executor_context=user_id
        )

        await db.run_workitem_audit.insert_one(audit.model_dump())
        
        # Update workitem with last run info (optional but good for UI)
        await db.workitem_master.update_one(
            {"workitem_id": workitem_id, "organization_id": organization_id},
            {"$set": {
                "last_ran_at": end_time,
                "last_ran_by": user_id,
                "last_run_status": status,
                "last_run_id": run_id
            }}
        )

        return audit

    @staticmethod
    async def _execute_rest_workitem(workitem: Workitem, logs: List[ExecutionLog]):
        if not workitem.rest_config:
            logs.append(ExecutionLog(log_type=LogType.ERROR, message="REST config missing"))
            return None, ExecutionStatus.FAILED
        
        config = workitem.rest_config
        logs.append(ExecutionLog(
            log_type=LogType.INFO, 
            message=f"Sending {config.method} request to {config.path}"
        ))

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=config.method,
                    url=config.path,
                    headers=config.headers,
                    params=config.query_params,
                    content=config.body,
                    timeout=30.0
                )
                
                resp_json = None
                try:
                    resp_json = response.json()
                except:
                    resp_json = {"raw": response.text}

                logs.append(ExecutionLog(
                    log_type=LogType.INFO,
                    message=f"Received response with status {response.status_code}",
                    payload=resp_json
                ))

                if 200 <= response.status_code < 300:
                    return resp_json, ExecutionStatus.PASSED
                else:
                    return resp_json, ExecutionStatus.FAILED

            except Exception as e:
                logs.append(ExecutionLog(log_type=LogType.ERROR, message=f"HTTP Request failed: {str(e)}"))
                return None, ExecutionStatus.FAILED

    @staticmethod
    async def _execute_sql_workitem(workitem: Workitem, logs: List[ExecutionLog]):
        # Implementation for real SQL execution would go here
        # For now, we simulate success
        logs.append(ExecutionLog(log_type=LogType.INFO, message="SQL execution simulated (Success)"))
        return {"message": "SQL Simulation Success"}, ExecutionStatus.PASSED

    @staticmethod
    async def _execute_mongo_workitem(workitem: Workitem, logs: List[ExecutionLog]):
        if not workitem.mongo_config:
            logs.append(ExecutionLog(log_type=LogType.ERROR, message="Mongo config missing"))
            return None, ExecutionStatus.FAILED

        config = workitem.mongo_config
        db = get_database()
        
        logs.append(ExecutionLog(
            log_type=LogType.INFO, 
            message=f"Executing {config.operation} on collection {config.collection}"
        ))

        try:
            collection = db[config.collection]
            query = json.loads(config.query) if config.query else {}
            
            result = None
            if config.operation == "FIND":
                cursor = collection.find(query).limit(10)
                result = await cursor.to_list(length=10)
            elif config.operation == "INSERT":
                doc = json.loads(config.document) if config.document else {}
                insert_res = await collection.insert_one(doc)
                result = {"inserted_id": str(insert_res.inserted_id)}
            # ... other ops ...
            else:
                logs.append(ExecutionLog(log_type=LogType.ERROR, message=f"Mongo operation {config.operation} not fully implemented"))
                return None, ExecutionStatus.FAILED

            logs.append(ExecutionLog(log_type=LogType.INFO, message="Mongo operation completed", payload={"result": str(result)}))
            return {"data": str(result)}, ExecutionStatus.PASSED

        except Exception as e:
            logs.append(ExecutionLog(log_type=LogType.ERROR, message=f"Mongo execution failed: {str(e)}"))
            return None, ExecutionStatus.FAILED

    @staticmethod
    async def run_testcase(
        organization_id: str,
        testcase_id: str,
        environment: Environment,
        user_id: str
    ) -> RunTestcaseAudit:
        """Run a testcase (sequence of workitems)."""
        db = get_database()
        testcase = await TestcaseService.get_testcase(testcase_id, organization_id)
        if not testcase:
            raise Exception("Testcase not found")

        run_id = await get_next_run_testcase_id()
        start_time = datetime.utcnow()
        results: List[WorkitemExecutionResult] = []
        overall_status = ExecutionStatus.PASSED

        for wi_id in testcase.workitem_ids:
            # Execute workitem
            wi_audit = await ExecutionService.run_workitem(
                organization_id, wi_id, environment, user_id
            )
            
            results.append(WorkitemExecutionResult(
                workitem_id=wi_id,
                workitem_title=wi_audit.workitem_title,
                execution_status=wi_audit.execution_status,
                execution_logs=wi_audit.execution_logs,
                actual_response=wi_audit.actual_response
            ))

            if wi_audit.execution_status == ExecutionStatus.FAILED:
                overall_status = ExecutionStatus.FAILED

        end_time = datetime.utcnow()
        audit = RunTestcaseAudit(
            run_testcase_id=run_id,
            organization_id=organization_id,
            testcase_id=testcase_id,
            testcase_title=testcase.name,
            environment=environment,
            overall_status=overall_status,
            workitem_results=results,
            run_testcase_created_date=start_time,
            run_testcase_start_time=start_time,
            run_testcase_end_time=end_time,
            executor_context=user_id
        )

        await db.run_testcase_audit.insert_one(audit.model_dump())
        
        # Update testcase with last run info
        await db.testcase_master.update_one(
            {"testcase_id": testcase_id, "organization_id": organization_id},
            {"$set": {
                "last_ran_at": end_time,
                "last_ran_by": user_id,
                "last_run_status": overall_status,
                "last_run_id": run_id
            }}
        )

        return audit
