"""
Content Experience Handlers - REST API for Content Operations

WHAT (Experience Plane): I provide REST endpoints for content operations
HOW (Handlers): I submit intents to Runtime and return results
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import base64

from utilities import get_logger


class UploadFileRequest(BaseModel):
    """Request to upload a file."""
    filename: str = Field(..., description="File name")
    tenant_id: str = Field(..., description="Tenant identifier")
    session_id: str = Field(..., description="Session identifier")
    file_data: str = Field(..., description="File data as base64 encoded string")


class UploadFileResponse(BaseModel):
    """Response from file upload."""
    success: bool
    file_id: Optional[str] = None
    file_reference: Optional[str] = None
    execution_id: Optional[str] = None
    error: Optional[str] = None


class CreateDataMashRequest(BaseModel):
    """Request to create a Data Mash."""
    content_refs: list[str] = Field(..., description="List of content references (file_ids or parsed_file_ids)")
    tenant_id: str = Field(..., description="Tenant identifier")
    session_id: str = Field(..., description="Session identifier")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Mash options (target_domain, confidence_level, etc.)")


class CreateDataMashResponse(BaseModel):
    """Response from Data Mash creation."""
    success: bool
    mash_id: Optional[str] = None
    mash_result: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    error: Optional[str] = None


def create_content_router(runtime_service: Any) -> APIRouter:
    """
    Create Content Experience router.
    
    Args:
        runtime_service: Runtime Service instance
    
    Returns:
        FastAPI router with content endpoints
    """
    router = APIRouter(prefix="/api/v1/content", tags=["content"])
    logger = get_logger("ContentExperience")
    
    @router.post("/upload", response_model=UploadFileResponse)
    async def upload_file(
        file: UploadFile = File(...),
        tenant_id: str = Form(...),
        session_id: str = Form(...)
    ):
        """
        Upload a file.
        
        Flow:
        1. Read file data
        2. Submit intent to Runtime: "content.upload"
        3. Return result
        """
        try:
            # Read file data
            file_data = await file.read()
            filename = file.filename or "uploaded_file"
            
            logger.info(f"File upload request: {filename} (tenant: {tenant_id}, session: {session_id})")
            
            # Submit intent to Runtime
            from symphainy_platform.runtime.runtime_service import SubmitIntentRequest
            
            intent_request = SubmitIntentRequest(
                intent_type="content.upload",
                realm="content",
                session_id=session_id,
                tenant_id=tenant_id,
                payload={
                    "file_data": base64.b64encode(file_data).decode('utf-8'),  # Base64 encode for JSON
                    "filename": filename,
                    "user_id": None  # Would come from auth context
                }
            )
            
            intent_response = await runtime_service.submit_intent(intent_request)
            
            if not intent_response.success:
                return UploadFileResponse(
                    success=False,
                    error=intent_response.error or "Intent submission failed"
                )
            
            # Get execution result
            execution_status = await runtime_service.get_execution_status(
                execution_id=intent_response.execution_id,
                tenant_id=tenant_id
            )
            
            if execution_status.success and execution_status.state:
                result = execution_status.state.get("result", {})
                return UploadFileResponse(
                    success=True,
                    file_id=result.get("file_id"),
                    file_reference=result.get("file_reference"),
                    execution_id=intent_response.execution_id
                )
            
            return UploadFileResponse(
                success=True,
                execution_id=intent_response.execution_id
            )
        
        except Exception as e:
            logger.error(f"File upload failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    @router.post("/data-mash/create", response_model=CreateDataMashResponse)
    async def create_data_mash(request: CreateDataMashRequest):
        """
        Create a Data Mash.
        
        Flow:
        1. Submit intent to Runtime: "data_mash.create"
        2. Return result
        """
        try:
            logger.info(f"Data Mash creation request: {len(request.content_refs)} content refs (tenant: {request.tenant_id})")
            
            # Submit intent to Runtime
            from symphainy_platform.runtime.runtime_service import SubmitIntentRequest
            
            intent_request = SubmitIntentRequest(
                intent_type="data_mash.create",
                realm="insights",
                session_id=request.session_id,
                tenant_id=request.tenant_id,
                payload={
                    "content_refs": request.content_refs,
                    "options": request.options
                }
            )
            
            intent_response = await runtime_service.submit_intent(intent_request)
            
            if not intent_response.success:
                return CreateDataMashResponse(
                    success=False,
                    error=intent_response.error or "Intent submission failed"
                )
            
            # Get execution result
            execution_status = await runtime_service.get_execution_status(
                execution_id=intent_response.execution_id,
                tenant_id=request.tenant_id
            )
            
            if execution_status.success and execution_status.state:
                result = execution_status.state.get("result", {})
                return CreateDataMashResponse(
                    success=True,
                    mash_id=result.get("mash_id"),
                    mash_result=result.get("mash_result"),
                    execution_id=intent_response.execution_id
                )
            
            return CreateDataMashResponse(
                success=True,
                execution_id=intent_response.execution_id
            )
        
        except Exception as e:
            logger.error(f"Data Mash creation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Data Mash creation failed: {str(e)}")
    
    return router
