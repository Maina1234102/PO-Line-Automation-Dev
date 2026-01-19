from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base

class ExcelUpload(Base):
    __tablename__ = "excel_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Processing") # Processing, Completed, Failed
    total_lines = Column(Integer, default=0)
    processed_lines = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    line_items = relationship("LineItemLog", back_populates="upload")

class LineItemLog(Base):
    __tablename__ = "line_item_logs"

    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("excel_uploads.id"))
    po_number = Column(String, index=True)
    line_number = Column(String, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String) # Success, Error
    error_message = Column(Text, nullable=True)
    
    # Optional: Store specific fields if requested "excel all fields"
    # For now, storing line number is key. If "all fields" are needed we might want a JSONB column
    # or specific columns. Given the request "excel all fields... and all more fields if you have any",
    # let's add a raw_data column to store the JSON representation of the line.
    raw_data = Column(Text, nullable=True) # JSON string of the line item

    upload = relationship("ExcelUpload", back_populates="line_items")
