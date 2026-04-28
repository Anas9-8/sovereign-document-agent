import os
import threading
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import router

load_dotenv()

static_dir = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    port = os.getenv("API_PORT", "8000")
    url = f"http://127.0.0.1:{port}"
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    yield


app = FastAPI(
    title="Sovereign Document Agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    static_file = static_dir / "index.html"
    if static_file.exists():
        return FileResponse(str(static_file))
    return {"message": "Sovereign Document Agent API", "docs": "/docs"}
