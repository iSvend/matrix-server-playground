from fastapi import FastAPI, Body, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
import threading
import shutil

from matrix import matrix_burst

# =========================
# PATH SETUP (SINGLE SOURCE OF TRUTH)
# =========================

BASE_DIR = Path(__file__).resolve().parent
HACK_DIR = BASE_DIR / "hack"
WEB_DIR  = BASE_DIR / "web"

# Ensure folders exist
HACK_DIR.mkdir(exist_ok=True)
WEB_DIR.mkdir(exist_ok=True)

app = FastAPI()

# =========================
# CORE ROUTES
# =========================

@app.get("/")
def hack_index():
    """Matrix console home"""
    return FileResponse(HACK_DIR / "index.html")


@app.get("/hack-trigger")
def hack_trigger():
    """Trigger Matrix terminal output"""
    threading.Thread(target=matrix_burst, daemon=True).start()
    return {"status": "ACCESS GRANTED"}


# =========================
# PROJECT MANAGEMENT
# =========================

@app.get("/projects")
def list_projects():
    projects = []
    for p in WEB_DIR.iterdir():
        if p.is_dir() and (p / "index.html").exists():
            projects.append(p.name)
    return {"projects": sorted(projects)}


@app.post("/projects/new/{project_name}")
def create_project(project_name: str):
    if not project_name.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid project name")

    project_dir = WEB_DIR / project_name

    if project_dir.exists():
        raise HTTPException(status_code=400, detail="Project already exists")

    project_dir.mkdir()

    (project_dir / "index.html").write_text(
        f"""<!DOCTYPE html>
<html>
<head>
    <title>{project_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

<h1>{project_name}</h1>
<p>This site was created from the Matrix.</p>

<script src="script.js"></script>
</body>
</html>
""",
        encoding="utf-8"
    )

    (project_dir / "style.css").write_text(
        """body {
    font-family: sans-serif;
    text-align: center;
    margin-top: 50px;
}
""",
        encoding="utf-8"
    )

    (project_dir / "script.js").write_text(
        """console.log("Hello from your new project!");""",
        encoding="utf-8"
    )

    return {"status": "created", "project": project_name}


@app.delete("/projects/delete/{project_name}")
def delete_project(project_name: str):
    if not project_name.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid project name")

    project_dir = WEB_DIR / project_name

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    shutil.rmtree(project_dir)
    return {"status": "deleted", "project": project_name}


# =========================
# IN-BROWSER EDITOR (PHASE 1 + 2)
# =========================

ALLOWED_EXTS = {".html", ".css", ".js"}

class FileUpdate(BaseModel):
    content: str


def safe_editor_path(project: str, file: str) -> Path:
    if not project.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid project name")

    if ".." in file or "/" in file or "\\" in file:
        raise HTTPException(status_code=400, detail="Invalid file path")

    path = (WEB_DIR / project / file).resolve()

    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if path.suffix.lower() not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    if WEB_DIR not in path.parents:
        raise HTTPException(status_code=400, detail="Invalid file location")

    return path


@app.get("/edit/file")
def read_file(
    project: str = Query(...),
    file: str = Query("index.html")
):
    path = safe_editor_path(project, file)
    return {"content": path.read_text(encoding="utf-8")}


@app.post("/edit/file")
def write_file(
    project: str = Query(...),
    file: str = Query("index.html"),
    data: FileUpdate = Body(...)
):
    path = safe_editor_path(project, file)
    path.write_text(data.content, encoding="utf-8")
    print("WRITE LENGTH:", len(data.content))
    print("WRITE PREVIEW:", data.content[:200])

    print("[EDITOR WRITE]", path)
    print("WEB_DIR AT RUNTIME:", WEB_DIR)
    return {"status": "saved"}


@app.get("/edit/list")
def list_files(project: str):
    if not project.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid project name")

    project_dir = (WEB_DIR / project).resolve()

    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    if WEB_DIR not in project_dir.parents:
        raise HTTPException(status_code=400, detail="Invalid project location")

    files = [
        f.name for f in project_dir.iterdir()
        if f.is_file() and f.suffix.lower() in ALLOWED_EXTS
    ]

    return {"files": sorted(files)}


# =========================
# STATIC FILE SERVERS (LAST)
# =========================

app.mount("/hack", StaticFiles(directory=HACK_DIR), name="hack")
app.mount("/web", StaticFiles(directory=WEB_DIR, html=True), name="web")