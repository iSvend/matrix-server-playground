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

    if (cmd === "help") {
        print("Commands:");
        print("  ls              list projects");
        print("  open <name>     open a project");
        print("  hack            trigger matrix");
        print("  clear           clear screen");
        return;
    }

    if (cmd === "clear") {
        terminal.innerText = "";
        return;
    }

    if (cmd === "hack") {
        fetch("/hack-trigger");
        print("ACCESS GRANTED");
        return;
    }

    if (cmd === "ls") {
        fetch("/projects")
            .then(r => r.json())
            .then(data => {
                if (data.projects.length === 0) {
                    print("No projects found.");
                } else {
                    data.projects.forEach(p => print(p));
                }
            });
        return;
    }

    if (cmd.startsWith("open ")) {
        const name = cmd.split(" ")[1];
        fetch("/projects")
            .then(r => r.json())
            .then(data => {
                if (data.projects.includes(name)) {
                    window.open(`/web/${name}/`, "_blank");
                    print(`Opening ${name}...`);
                } else {
                    print("Project not found.");
                }
            });
        return;
    }

    print("Unknown command.");
}
