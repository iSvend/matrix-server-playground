let pendingDelete = null;

const terminal = document.getElementById("terminal");
const input = document.getElementById("command");

function print(line = "") {
    terminal.innerText += line + "\n";
    terminal.scrollTop = terminal.scrollHeight;
}

print("WELCOME TO THE MATRIX");
print("Type 'help' for commands.");

input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        runCommand();
    }
});

function runCommand() {
    const cmd = input.value.trim();
    input.value = "";

    print("> " + cmd);

    if (!cmd) return;

    // ---- HELP ----
    if (cmd === "help") {
        print("Commands:");
        print("  help               show commands");
        print("  ls                 list projects");
        print("  open <name>        open a project");
        print("  new <name>         create a new project");
        print("  delete <name>      delete a project");
        print("  clear              clear screen");
        print("  hack               ----");
        return;
    }

    // ---- CLEAR ----
    if (cmd === "clear") {
        terminal.innerText = "";
        return;
    }

    // ---- HACK ----
    if (cmd === "hack") {
        fetch("/hack-trigger");
        print("ACCESS GRANTED");
        return;
    }

    // ---- LIST PROJECTS ----
    if (cmd === "ls") {
        fetch("/projects")
            .then(r => r.json())
            .then(data => {
                if (!data.projects.length) {
                    print("No projects found.");
                } else {
                    data.projects.forEach(p => print(p));
                }
            });
        return;
    }

    // ---- NEW PROJECT ----
    if (cmd.startsWith("new ")) {
        const name = cmd.split(" ")[1];

        fetch(`/projects/new/${name}`, { method: "POST" })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    print(`ERROR: ${data.error}`);
                } else {
                    print(`Project '${name}' created.`);
                    print("Type 'ls' to see it.");
                }
            });

        return;
    }

    // ---- DELETE PROJECT (STEP 1) ----
    if (cmd.startsWith("delete ")) {
        const name = cmd.split(" ")[1];

        pendingDelete = name;

        print(`WARNING: This will permanently delete '${name}'`);
        print(`Type: confirm delete ${name}`);

        return;
    }

    // ---- CONFIRM DELETE (STEP 2) ----
    if (cmd.startsWith("confirm delete ")) {
        const name = cmd.replace("confirm delete ", "").trim();

        if (!pendingDelete) {
            print("No delete operation pending.");
            return;
        }

        if (name !== pendingDelete) {
            print("Confirmation name does not match. Delete cancelled.");
            pendingDelete = null;
            return;
        }

        fetch(`/projects/delete/${name}`, { method: "DELETE" })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    print(`ERROR: ${data.error}`);
                } else {
                    print(`Project '${name}' deleted.`);
                }
            })
            .catch(() => {
                print("ERROR: Failed to delete project.");
            });

        pendingDelete = null;
        return;
    }

    // ---- CANCEL DELETE ----
    if (cmd === "cancel") {
        if (pendingDelete) {
            print(`Delete of '${pendingDelete}' cancelled.`);
            pendingDelete = null;
        } else {
            print("Nothing to cancel.");
        }
        return;
    }



    // ---- OPEN PROJECT ----
    if (cmd.startsWith("open ")) {
        const name = cmd.split(" ")[1];
        window.open(`/web/${name}/`, "_blank");
        return;
    }

    // ---- FALLBACK ----
    print("Unknown command. Type 'help'.");
}

function runHack() {
    input.value = "hack";
    runCommand();
}
