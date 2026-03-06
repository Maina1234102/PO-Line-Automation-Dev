import uvicorn
# Import the app to ensure it's loaded, but uvicorn will likely load by string import or object
from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="172.16.10.130", port=8000)
