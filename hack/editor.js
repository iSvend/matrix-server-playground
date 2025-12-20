function qs(name) {
    return new URLSearchParams(window.location.search).get(name);
}

const sidebar = document.getElementById("sidebar");
const preview = document.getElementById("preview");
let currentFile = qs("file") || "index.html";
const project = qs("project");
const file = "index.html";
document.getElementById("projectName").textContent = project || "???";
const statusEl = document.getElementById("status");
const cm = CodeMirror.fromTextArea(
    document.getElementById("editor"),
    {
        lineNumbers: true,
        mode: "htmlmixed",
        theme: "default"
    }
);

async function loadFile() {
    setMode(currentFile);
    const res = await fetch(`/edit/file?project=${project}&file=${currentFile}`);
    const data = await res.json();
    cm.setValue(data.content || "");
    preview.src = `/web/${project}/index.html?t=${Date.now()}`;

}

async function saveFile() {
    console.log("EDITOR SAVE LENGTH:", cm.getValue().length);
    console.log("EDITOR SAVE PREVIEW:", cm.getValue().slice(0, 200));

    await fetch(`/edit/file?project=${project}&file=${currentFile}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ content: cm.getValue() })
    });
    preview.src = "about:blank";
    setTimeout(() => {
        preview.src = `/web/${project}/index.html?t=${Date.now()}`;
    }, 50);

}

async function loadFileList() {
    const res = await fetch(`/edit/list?project=${encodeURIComponent(project)}`);
    const data = await res.json();

    sidebar.innerHTML = "";

    if (!res.ok || !data.files) {
        const msg = data.detail || "Failed to load file list";
        sidebar.textContent = msg;
        console.error("File list error:", data);
        return;
    }

    data.files.forEach(f => {
        const el = document.createElement("div");
        el.textContent = f;
        el.style.padding = "6px";
        el.style.cursor = "pointer";
        el.onclick = () => {
            currentFile = f;
            loadFile();
        };
        sidebar.appendChild(el);
    });
}


function setMode(file) {
    if (file.endsWith(".css")) cm.setOption("mode", "css");
    else if (file.endsWith(".js")) cm.setOption("mode", "javascript");
    else cm.setOption("mode", "htmlmixed");
}

document.getElementById("saveBtn").onclick = saveFile;
document.getElementById("openBtn").onclick = () => {
    window.open(`/web/${project}/`, "_blank");
};

loadFileList();
loadFile();