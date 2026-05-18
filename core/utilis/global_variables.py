import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://kwenda:936042180S@db:5432/mydatabase"
)
