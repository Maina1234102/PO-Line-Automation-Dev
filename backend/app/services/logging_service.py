from sqlalchemy.orm import Session
from backend.app.models.logging_models import ExcelUpload, LineItemLog
from datetime import datetime
import json

class LoggingService:
    def create_upload(self, db: Session, filename: str, total_lines: int) -> ExcelUpload:
        upload = ExcelUpload(
            filename=filename,
            total_lines=total_lines,
            status="Processing"
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return upload

    def update_upload_status(self, db: Session, upload_id: int, status: str, success_count: int, error_count: int):
        upload = db.query(ExcelUpload).filter(ExcelUpload.id == upload_id).first()
        if upload:
            upload.status = status
            upload.processed_lines = success_count + error_count
            upload.success_count = success_count
            upload.error_count = error_count
            db.commit()

    def log_line_item(self, db: Session, upload_id: int, po_number: str, line_data: dict, status: str, error_msg: str = None):
        line_item = LineItemLog(
            upload_id=upload_id,
            po_number=po_number,
            line_number=str(line_data.get("LineNumber", "")),
            status=status,
            error_message=error_msg,
            end_time=datetime.utcnow(),
            raw_data=json.dumps(line_data, default=str)
        )
        db.add(line_item)
        db.commit()
        
    def increment_download_count(self, db: Session, upload_id: int):
        upload = db.query(ExcelUpload).filter(ExcelUpload.id == upload_id).first()
        if upload:
            upload.download_count += 1
            db.commit()

logging_service = LoggingService()
