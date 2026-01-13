import uvicorn
# Import the app to ensure it's loaded, but uvicorn will likely load by string import or object
from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
