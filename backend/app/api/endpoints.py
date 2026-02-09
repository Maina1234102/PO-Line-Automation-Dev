from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from backend.app.schemas.po_models import POSubmission
from backend.app.schemas.user_schemas import UserLogin
from backend.app.models.logging_models import ExcelUpload # Removed User import
from backend.app.services.oracle import oracle_service
from backend.app.services.logging_service import logging_service
from backend.app.core.database import get_db
import logging
import base64

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBasic()

def get_oracle_auth(credentials: HTTPBasicCredentials = Depends(security)) -> tuple:
    return (credentials.username, credentials.password)

@router.post("/login")
async def login(user_credentials: UserLogin):
    # Verify against Oracle
    auth = (user_credentials.email, user_credentials.password)
    is_valid = oracle_service.verify_credentials(auth)
    
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid Oracle credentials")
        
    return {"status": "success", "message": "Login successful", "user": {"email": user_credentials.email}}

@router.post("/process-lines")
async def process_lines(submission: POSubmission, db: Session = Depends(get_db), auth: tuple = Depends(get_oracle_auth)):
    logger.info(f"Received submission for PO: {submission.po_number} with {len(submission.lines)} lines")
    
    # Create Upload Log
    upload_record = logging_service.create_upload(
        db, 
        filename=submission.excel_filename or "Unknown", 
        total_lines=len(submission.lines),
        po_number=submission.po_number
    )

    try:
        # Step 1: Get PO Header ID
        header_id = oracle_service.get_po_header_id(submission.po_number, auth=auth)
        if not header_id:
            error_msg = f"PO Number {submission.po_number} not found in Oracle."
            logging_service.update_upload_status(db, upload_record.id, "Failed", 0, len(submission.lines))
            # Log all lines as failed due to missing PO? Or just fail the upload?
            # Let's just fail the upload.
            raise HTTPException(status_code=404, detail=error_msg)
        
        logger.info(f"Found POHeaderId: {header_id}")

        # Step 2: Create Line Items
        created_count = 0
        errors = []

        for line in submission.lines:
            # Prepare line data for logging (include PO Header ID if useful)
            line_data = line.model_dump(by_alias=True)
            line_data['POHeaderId'] = header_id
            
            success, error_msg = oracle_service.create_line_item(header_id, line, auth=auth)
            
            if success:
                created_count += 1
                logging_service.log_line_item(db, upload_record.id, submission.po_number, line_data, "Success")
            else:
                errors.append(f"Line {line.line_number}: {error_msg}")
                logging_service.log_line_item(db, upload_record.id, submission.po_number, line_data, "Error", error_msg)

        status = "Completed" if len(errors) == 0 else "Completed (Partial)"
        if created_count == 0 and len(errors) > 0:
            status = "Failed"

        logging_service.update_upload_status(db, upload_record.id, status, created_count, len(errors))

        return {
            "status": "success" if len(errors) == 0 else "partial_success",
            "message": f"Processed PO {submission.po_number}. Created {created_count}/{len(submission.lines)} lines.",
            "poHeaderId": header_id,
            "errors": errors,
            "uploadId": upload_record.id
        }

    except HTTPException as he:
        # Update upload status if not already set? 
        # Ideally we should wrap this to ensure status is updated on crash
        logging_service.update_upload_status(db, upload_record.id, "Failed", 0, 0)
        raise he
    except Exception as e:
        logger.error(f"Error processing PO: {str(e)}")
        logging_service.update_upload_status(db, upload_record.id, "Failed", 0, 0)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log-download")
async def log_download(start_log: dict, db: Session = Depends(get_db), auth: tuple = Depends(get_oracle_auth)):
    # Expecting { "uploadId": 123 }
    upload_id = start_log.get("uploadId")
    if upload_id:
        logging_service.increment_download_count(db, upload_id)
        return {"status": "success"}
    if upload_id:
        logging_service.increment_download_count(db, upload_id)
        return {"status": "success"}
    return {"status": "ignored"}

@router.get("/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db), auth: tuple = Depends(get_oracle_auth)):
    return logging_service.get_dashboard_metrics(db)

@router.get("/dashboard/recent-uploads")
def get_recent_uploads(db: Session = Depends(get_db), auth: tuple = Depends(get_oracle_auth)):
    uploads = logging_service.get_recent_uploads(db, limit=20)
    return uploads

@router.get("/dashboard/upload/{upload_id}")
def get_upload_details(upload_id: int, db: Session = Depends(get_db), auth: tuple = Depends(get_oracle_auth)):
    # Simple fetch for now, can be expanded to return line logs if needed
    upload = db.query(ExcelUpload).filter(ExcelUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return upload

@router.get("/")
def read_root():
    return {"message": "PO Line Import Backend is running (Refactored)"}
