from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import create_engine

from app.models.base.base_model import Base
from app.config import settings

# Membuat engine SQLAlchemy untuk berkomunikasi dengan DB
# Gunakan engine ini untuk membuat query
engine = create_engine(settings.database_url)


# Kode setup yang dipanggil sebelum aplikasi berjalan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Memastikan bahwa database memiliki setiap tabel yang didefinisikan
    # WARNING: Metadata.create_all() tidak melakukan update skema apabila tabel sudah ada di DB
    Base.metadata.create_all(engine)

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}
