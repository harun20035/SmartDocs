from fastapi import FastAPI
from app.database import engine

app = FastAPI(title="SmartDocs API")

@app.get("/")
def root():
    return {"message": "SmartDocs backend radi 🚀"}

@app.get("/db-test")
def db_test():
    try:
        conn = engine.connect()
        conn.close()
        return {"status": "DB connection OK ✅"}
    except Exception as e:
        return {"status": "DB connection FAILED ❌", "error": str(e)}