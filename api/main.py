from fastapi import FastAPI, Depends
from api.routes import coupa, mistral
from dependencies.auth import verify_api_key

app = FastAPI(root_path="/invoice-audit", dependencies=[Depends(verify_api_key)])

app.include_router(coupa.router, prefix="/coupa")
app.include_router(mistral.router, prefix="/mistral")

@app.get("/health")
def health_check():
    return {"status": "ok"}
