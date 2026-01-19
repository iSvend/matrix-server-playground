from fastapi import FastAPI, Body, HTTPException, Query, UploadFile, File, Form
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
    # Allow simple, safe names only
    if not project_name.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid project name")

    project_dir = WEB_DIR / project_name

    if project_dir.exists():
        raise HTTPException(status_code=400, detail="Project already exists")

    project_dir.mkdir()

    index_html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>{project_name}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <!-- Styles -->
        <link rel="stylesheet" href="style.css" />
    </head>
    <body>

    <header class="site-header">
        <div class="container">
            <h1>{project_name}</h1>
            <p class="tagline">Built inside the Matrix</p>
        </div>
    </header>

    <main class="container">
        <section class="card">
            <h2>Welcome 👋</h2>
            <p>
                This is your new website.  
                Edit the HTML, CSS, and JavaScript directly from the Matrix editor.
            </p>

            <button id="actionBtn">Click me</button>
        </section>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>© {project_name}</p>
        </div>
    </footer>

    <script src="script.js"></script>
    </body>
    </html>
    """

    style_css = """/* === Modern Starter Styles === */

    :root {
        --bg: #0f172a;
        --card: #111827;
        --text: #e5e7eb;
        --muted: #9ca3af;
        --accent: #22c55e;
        --border: #1f2933;
    }

    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
            Roboto, Ubuntu, Cantarell, "Helvetica Neue", Arial, sans-serif;
        background: linear-gradient(180deg, #020617, var(--bg));
        color: var(--text);
        line-height: 1.6;
    }

    /* Layout */
    .container {
        max-width: 900px;
        margin: 0 auto;
        padding: 24px;
    }

    /* Header */
    .site-header {
        border-bottom: 1px solid var(--border);
    }

    .site-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }

    .tagline {
        margin-top: 8px;
        color: var(--muted);
    }

    /* Card */
    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 32px;
        margin-top: 40px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .card h2 {
        margin-top: 0;
    }

    /* Button */
    button {
        margin-top: 20px;
        padding: 12px 20px;
        font-size: 1rem;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        background: var(--accent);
        color: #022c22;
        font-weight: 600;
        transition: transform 0.1s ease, box-shadow 0.1s ease;
    }

    button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.35);
    }

    /* Footer */
    .site-footer {
        margin-top: 80px;
        border-top: 1px solid var(--border);
        color: var(--muted);
        font-size: 0.9rem;
    }
    """

    script_js = """// === Modern Starter Script ===

    console.log("Site loaded");

    document.getElementById("actionBtn").addEventListener("click", () => {
        alert("Hello from the Matrix 👾");
    });
    """


    (project_dir / "index.html").write_text(index_html, encoding="utf-8")
    (project_dir / "style.css").write_text(style_css, encoding="utf-8")
    (project_dir / "script.js").write_text(script_js, encoding="utf-8")

    return {
        "status": "created",
        "project": project_name,
        "files": ["index.html", "style.css", "script.js"]
    }

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

# =========================
# FOLDER UPLOAD (DIRECTORY UPLOAD)
# =========================

UPLOAD_ALLOWED_EXTS = {
    ".html", ".css", ".js",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".txt", ".json", ".map"
}

def _is_safe_project_name(name: str) -> bool:
    return bool(name) and name.replace("-", "").replace("_", "").isalnum()

def _safe_relpath(rel: str) -> Path:
    """
    Convert a client-provided relative path to a safe Path (no .., no absolute).
    """
    rel = rel.replace("\\", "/").lstrip("/")  # normalize
    if not rel or rel.startswith("../") or "/../" in rel or rel == "..":
        raise HTTPException(status_code=400, detail="Invalid relative path")
    p = Path(rel)
    if p.is_absolute():
        raise HTTPException(status_code=400, detail="Absolute paths not allowed")
    # Also block any '..' segments
    if any(part == ".." for part in p.parts):
        raise HTTPException(status_code=400, detail="Invalid path traversal")
    return p

@app.post("/upload/project")
async def upload_project_folder(
    project_name: str = Form(...),
    root_folder: str = Form(...),
    overwrite: bool = Form(False),
    files: list[UploadFile] = File(...)
):
    """
    Upload a whole folder (from <input webkitdirectory>) and store it as /web/<project_name>/...
    Client sends file.filename like: "<root_folder>/subdir/file.ext"
    """
    if not _is_safe_project_name(project_name):
        raise HTTPException(status_code=400, detail="Invalid project name")

    if not root_folder:
        raise HTTPException(status_code=400, detail="Missing root folder")

    dest_dir = (WEB_DIR / project_name).resolve()

    # Safety: ensure dest_dir is under WEB_DIR
    if WEB_DIR.resolve() not in dest_dir.parents:
        raise HTTPException(status_code=400, detail="Invalid destination")

    if dest_dir.exists():
        if not overwrite:
            raise HTTPException(status_code=400, detail="Project already exists (enable overwrite)")
        shutil.rmtree(dest_dir)

    dest_dir.mkdir(parents=True, exist_ok=True)

    saved = 0
    skipped = 0

    for uf in files:
        # uf.filename will contain the relative path (often includes the chosen folder root)
        rel = uf.filename.replace("\\", "/")

        # Strip the selected root folder prefix if present
        prefix = root_folder.strip("/").strip("\\") + "/"
        if rel.startswith(prefix):
            rel = rel[len(prefix):]

        # If the browser sends just a filename sometimes, keep it
        rel_path = _safe_relpath(rel)

        # Extension allowlist (skip silently or error; here we skip)
        ext = rel_path.suffix.lower()
        if ext and ext not in UPLOAD_ALLOWED_EXTS:
            skipped += 1
            continue

        out_path = (dest_dir / rel_path).resolve()

        # Ensure output stays inside dest_dir
        if dest_dir not in out_path.parents and out_path != dest_dir:
            raise HTTPException(status_code=400, detail="Invalid upload path")

        out_path.parent.mkdir(parents=True, exist_ok=True)

        data = await uf.read()
        out_path.write_bytes(data)
        saved += 1

    # Helpful: ensure an index.html exists at project root (optional)
    has_index = (dest_dir / "index.html").exists()

    return {
        "status": "ok",
        "project": project_name,
        "saved_files": saved,
        "skipped_files": skipped,
        "has_index": has_index
    }

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