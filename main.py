from fastapi import FastAPI
from apis.report_endpoints import router as report_router

app = FastAPI()
app.include_router(report_router)
