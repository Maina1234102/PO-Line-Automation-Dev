import sys
import os
from sqlalchemy import text, inspect

# Ensure we can import the backend modules
sys.path.append(os.getcwd())

from backend.app.core.database import SessionLocal, engine

def show_db_status():
    print("--- Database Structure ---")
    try:
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(f"Tables found: {tables}")
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return

    db = SessionLocal()
    try:
        print("\n--- Recent Uploads (excel_uploads) ---")
        result = db.execute(text("SELECT id, filename, status, total_lines, download_count FROM excel_uploads ORDER BY id DESC LIMIT 5"))
        rows = result.fetchall()
        if not rows:
            print("No records found.")
        for row in rows:
            print(row)

        print("\n--- Recent Line Logs (line_item_logs) ---")
        # Selecting specific columns for readability
        result_lines = db.execute(text("SELECT id, upload_id, po_number, line_number, status, error_message FROM line_item_logs ORDER BY id DESC LIMIT 5"))
        rows_lines = result_lines.fetchall()
        if not rows_lines:
            print("No records found.")
        for row in rows_lines:
            print(row)
            
    except Exception as e:
        print(f"Error querying data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    show_db_status()
