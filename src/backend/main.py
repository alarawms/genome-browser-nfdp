import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.backend.data_loader import DataStore
from src.backend.routers import species, qtls, search

DATA_DIR = os.environ.get("DATA_DIR", "data")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.store = DataStore(data_dir=DATA_DIR)
    yield


app = FastAPI(title="Saudi Livestock Genome Browser API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(species.router)
app.include_router(qtls.router)
app.include_router(search.router)

# Mount data directory for JBrowse 2 static file access
data_path = os.path.abspath(DATA_DIR)
if os.path.isdir(data_path):
    app.mount("/data", StaticFiles(directory=data_path), name="data")
