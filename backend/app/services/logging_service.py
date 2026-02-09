from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.logging_models import ExcelUpload, LineItemLog
from datetime import datetime
import json

class LoggingService:
    def create_upload(self, db: Session, filename: str, total_lines: int, po_number: str = None) -> ExcelUpload:
        upload = ExcelUpload(
            filename=filename,
            po_number=po_number,
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

    def get_recent_uploads(self, db: Session, limit: int = 20):
        return db.query(ExcelUpload).order_by(ExcelUpload.created_at.desc()).limit(limit).all()

    def get_dashboard_metrics(self, db: Session):
        total_uploads = db.query(ExcelUpload).count()
        
        # Calculate success rate based on lines or uploads? Let's do uploads for now
        # "Success" if status is "Completed"
        successful_uploads = db.query(ExcelUpload).filter(ExcelUpload.status == "Completed").count()
        success_rate = (successful_uploads / total_uploads * 100) if total_uploads > 0 else 0
        
        # Total lines processed
        total_lines_processed = db.query(func.sum(ExcelUpload.processed_lines)).scalar() or 0
        
        # Pending/Failed
        failed_uploads = db.query(ExcelUpload).filter(ExcelUpload.status == "Failed").count()
        
        # Today's uploads
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_uploads = db.query(ExcelUpload).filter(ExcelUpload.created_at >= today_start).count()

        return {
            "totalUploads": total_uploads,
            "successRate": round(success_rate, 1),
            "totalLinesProcessed": total_lines_processed,
            "failedUploads": failed_uploads,
            "todayUploads": today_uploads
        }

logging_service = LoggingService()
