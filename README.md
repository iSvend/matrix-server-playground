# 🟢 Portable Matrix Server

A playful, hacker-style **local web server + Matrix terminal experience**, built as a **fully portable Windows app**.

This project runs a FastAPI web server locally, displays a Matrix-inspired terminal UI in the browser, and triggers classic Matrix rain effects in the system console. It’s designed as a fun learning playground for web development, commands, and how real servers work — with extra green glow.

---

## ✨ Features

- 🚀 Local FastAPI web server  
- 🖥️ Matrix-style terminal UI in the browser  
- 🌧️ Matrix rain + ASCII finale in the console  
- ⌨️ Typed commands (no mouse required)  
- 📂 Auto-discovers web projects  
- 🧱 Scaffold new projects from the terminal  
- 🗑️ Delete projects with confirmation  
- 📦 Portable Python runtime included  
- 🪟 One-click Windows launcher (`.exe`)  

No global Python install required to **run** the app.

---

## 📁 Project Structure

```
MatrixServer/
│
├── app.py                 # FastAPI backend
├── matrix.py              # Terminal Matrix rain + ASCII effects
├── launcher.py            # Windows launcher (used to build EXE)
├── build_launcher.bat     # One-click build script
│
├── hack/                  # Matrix UI (HTML/CSS/JS)
│   └── index.html
│
├── web/                   # User web projects live here
│   └── index.html         # Project landing page
│
├── python/                # Embedded Python runtime (portable)
│
├── .gitignore
└── README.md
```

---

## 🧠 How It Works

### 🟩 Matrix UI (`/hack`)
- Browser-based terminal interface  
- Accepts typed commands like a fake OS shell  
- Can trigger backend effects (Matrix rain, project actions)

### 🟦 Web Projects (`/web`)
- Each subfolder inside `/web` is treated as a project  
- Each project must contain an `index.html`  
- Projects can be listed, opened, created, and deleted  

---

## ⌨️ Available Commands

| Command | Description |
|------|------------|
| `help` | Show available commands |
| `ls` | List all projects in `/web` |
| `open ProjectName` | Open `/web/ProjectName/index.html` |
| `new ProjectName` | Scaffold a new web project |
| `delete ProjectName` | Delete a project (with confirmation) |
| `hack` | Trigger Matrix rain + ASCII finale |

🟢 The **HACK** button in the UI runs the same action as typing `hack`.

---

## 🔌 Backend Endpoints (FastAPI)

| Endpoint | Purpose |
|------|------|
| `/` | Loads the Matrix UI |
| `/hack-trigger` | Triggers Matrix rain in console |
| `/projects` | Returns list of web projects |
| `/web/{project}` | Serves project index files |

---

## 🧪 Run in Development Mode (No EXE)

```
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Then open:

```
http://127.0.0.1:8000
```

---

## 🚀 Run the Portable App (EXE)

```
dist\launcher\launcher.exe
```

---

## 🏗️ Build the Launcher EXE (One Click)

### Build Prerequisites
- Python installed  
- PyInstaller installed  

```
python -m pip install pyinstaller
```

### Build

Double-click:

```
build_launcher.bat
```

---

## 🚫 Git Ignore Notes

```
/dist
/build
*.spec
```

---

## 🟩 Final Note

Break it. Hack it. Extend it.

**Welcome to the Matrix.** 🟢💻
