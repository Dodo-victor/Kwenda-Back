from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import tables
from core.database.db import engine, Base
from routes.admin.auth_route import router as auth_router
from routes.admin.plan_router import router as plan_router
from routes.admin.admin_route import router as admin_router
from routes.admin.queue_router import router as queue_router


app = FastAPI()


origins = ["http://localhost", "http://localhost:3000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(plan_router, prefix="/admin/plans", tags=["plans"])
app.include_router(queue_router, prefix="/admin/queue", tags=["queue"])

print("Connected to the database")
tables.start_tables()
print("Tables created successfully")
