from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from matrix import matrix_burst
import threading
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HACK_DIR = os.path.join(BASE_DIR, "hack")
WEB_DIR  = os.path.join(BASE_DIR, "web")

app = FastAPI()

# =========================
# ROUTES (must come FIRST)
# =========================

@app.get("/")
def hack_index():
    """Matrix console home"""
    return FileResponse(os.path.join(HACK_DIR, "index.html"))


@app.get("/web")
@app.get("/web/")
def web_root():
    """Root web workspace"""
    return FileResponse(os.path.join(WEB_DIR, "index.html"))


@app.get("/web/{project}")
@app.get("/web/{project}/")
def web_project(project: str):
    """Serve a project's index.html"""
    index_file = os.path.join(WEB_DIR, project, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)

    return JSONResponse(
        status_code=404,
        content={"error": "Project not found"}
    )


@app.get("/hack-trigger")
def hack_trigger():
    """Trigger Matrix terminal output"""
    threading.Thread(target=matrix_burst, daemon=True).start()
    return {"status": "ACCESS GRANTED"}


@app.get("/projects")
def list_projects():
    """List valid web projects"""
    projects = []

    if not os.path.exists(WEB_DIR):
        return JSONResponse({"projects": projects})

    for name in os.listdir(WEB_DIR):
        path = os.path.join(WEB_DIR, name)
        if os.path.isdir(path):
            index_file = os.path.join(path, "index.html")
            if os.path.exists(index_file):
                projects.append(name)

    return JSONResponse({"projects": projects})


# =========================
# STATIC FILE SERVERS (LAST)
# =========================

# Matrix UI assets (CSS/JS)
app.mount("/hack", StaticFiles(directory=HACK_DIR), name="hack")

# Web project assets (CSS/JS/images inside projects)
app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")
