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

@app.post("/projects/new/{project_name}")
def create_project(project_name: str):
    # Basic safety: allow simple names only
    if not project_name.replace("-", "").replace("_", "").isalnum():
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid project name"}
        )

    project_dir = os.path.join(WEB_DIR, project_name)

    if os.path.exists(project_dir):
        return JSONResponse(
            status_code=400,
            content={"error": "Project already exists"}
        )

    os.makedirs(project_dir)

    # --- Starter files ---
    index_html = f"""<!DOCTYPE html>
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
"""

    style_css = """body {
    font-family: sans-serif;
    text-align: center;
    margin-top: 50px;
}
"""

    script_js = """console.log("Hello from your new project!");
"""

    with open(os.path.join(project_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    with open(os.path.join(project_dir, "style.css"), "w", encoding="utf-8") as f:
        f.write(style_css)

    with open(os.path.join(project_dir, "script.js"), "w", encoding="utf-8") as f:
        f.write(script_js)

    return {"status": "created", "project": project_name}

# delete project
import shutil

@app.delete("/projects/delete/{project_name}")
def delete_project(project_name: str):
    # Same name safety rules as creation
    if not project_name.replace("-", "").replace("_", "").isalnum():
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid project name"}
        )

    project_dir = os.path.join(WEB_DIR, project_name)

    if not os.path.exists(project_dir):
        return JSONResponse(
            status_code=404,
            content={"error": "Project not found"}
        )

    # Extra safety: ensure it's inside /web
    if not os.path.commonpath([WEB_DIR, project_dir]) == WEB_DIR:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid delete path"}
        )

    shutil.rmtree(project_dir)

    return {"status": "deleted", "project": project_name}


# =========================
# STATIC FILE SERVERS (LAST)
# =========================

# Matrix UI assets (CSS/JS)
app.mount("/hack", StaticFiles(directory=HACK_DIR), name="hack")

# Web project assets (CSS/JS/images inside projects)
app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")
