const folderInput = document.getElementById("folderInput");
const projectNameEl = document.getElementById("projectName");
const overwriteEl = document.getElementById("overwrite");
const uploadBtn = document.getElementById("uploadBtn");
const openBtn = document.getElementById("openBtn");
const statusEl = document.getElementById("status");

let rootFolder = null;

function setStatus(msg) {
  statusEl.textContent = msg;
}

folderInput.addEventListener("change", () => {
  const files = Array.from(folderInput.files || []);
  if (!files.length) {
    uploadBtn.disabled = true;
    openBtn.disabled = true;
    setStatus("");
    return;
  }

  // Detect root folder name from webkitRelativePath
  const first = files[0];
  const rel = first.webkitRelativePath || first.name;
  rootFolder = rel.split("/")[0];

  // Auto-fill project name if empty
  if (!projectNameEl.value.trim()) {
    // make it safer: remove spaces
    projectNameEl.value = rootFolder.replace(/\s+/g, "");
  }

  uploadBtn.disabled = false;
  openBtn.disabled = true;

  setStatus(`Selected folder: ${rootFolder}\nFiles: ${files.length}`);
});

uploadBtn.addEventListener("click", async () => {
  const files = Array.from(folderInput.files || []);
  const projectName = projectNameEl.value.trim();
  const overwrite = overwriteEl.checked;

  if (!files.length) return;
  if (!projectName) {
    setStatus("ERROR: Please enter a project name.");
    return;
  }
  if (!rootFolder) {
    setStatus("ERROR: Could not detect root folder name.");
    return;
  }

  uploadBtn.disabled = true;
  setStatus("Uploading...");

  const fd = new FormData();
  fd.append("project_name", projectName);
  fd.append("root_folder", rootFolder);
  fd.append("overwrite", overwrite ? "true" : "false");

  // Important: keep relative paths. Browsers will send filename from webkitRelativePath.
  // Most servers receive that relative path in UploadFile.filename.
  for (const f of files) {
    fd.append("files", f, f.webkitRelativePath || f.name);
  }

  try {
    const res = await fetch("/upload/project", {
      method: "POST",
      body: fd
    });

    const data = await res.json();

    if (!res.ok) {
      setStatus(`ERROR: ${data.detail || "Upload failed"}`);
      uploadBtn.disabled = false;
      return;
    }

    setStatus(
      `✅ Upload complete\n` +
      `Project: ${data.project}\n` +
      `Saved files: ${data.saved_files}\n` +
      `Skipped files: ${data.skipped_files}\n` +
      `Has index.html: ${data.has_index}`
    );

    openBtn.disabled = false;
    openBtn.onclick = () => window.open(`/web/${encodeURIComponent(projectName)}/`, "_blank");
  } catch (err) {
    setStatus("ERROR: Upload failed (network/server).");
    uploadBtn.disabled = false;
  }
});