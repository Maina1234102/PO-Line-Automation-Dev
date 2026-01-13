from fastapi import APIRouter, HTTPException
from backend.app.schemas.po_models import POSubmission
from backend.app.services.oracle import oracle_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/process-lines")
async def process_lines(submission: POSubmission):
    logger.info(f"Received submission for PO: {submission.po_number} with {len(submission.lines)} lines")
    
    try:
        # Step 1: Get PO Header ID
        header_id = oracle_service.get_po_header_id(submission.po_number)
        if not header_id:
            raise HTTPException(status_code=404, detail=f"PO Number {submission.po_number} not found in Oracle.")
        
        logger.info(f"Found POHeaderId: {header_id}")

        # Step 2: Create Line Items
        created_count = 0
        errors = []

        for line in submission.lines:
            success, error_msg = oracle_service.create_line_item(header_id, line)
            if success:
                created_count += 1
            else:
                errors.append(f"Line {line.line_number}: {error_msg}")

        return {
            "status": "success" if len(errors) == 0 else "partial_success",
            "message": f"Processed PO {submission.po_number}. Created {created_count}/{len(submission.lines)} lines.",
            "poHeaderId": header_id,
            "errors": errors
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing PO: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def read_root():
    return {"message": "PO Line Import Backend is running (Refactored)"}
