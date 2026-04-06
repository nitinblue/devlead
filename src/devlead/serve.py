"""DevLead local server — interactive dashboard with write-back to md files.

Serves the HTML dashboard on localhost and handles POST requests
to update governance files. Zero external dependencies — stdlib only.
"""

import json
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs

from devlead import ui
from devlead.dashboard import write_dashboard
from devlead.doc_parser import parse_table


class DevLeadHandler(SimpleHTTPRequestHandler):
    """Handles GET (serve dashboard) and POST (update md files)."""

    project_dir: Path = Path(".")

    def do_GET(self) -> None:
        if self.path == "/" or self.path == "/dashboard":
            self._serve_dashboard()
        elif self.path == "/api/status":
            self._json_response({"status": "ok", "project": str(self.project_dir)})
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        action = data.get("action", "")

        if action == "accept_tbo":
            result = _accept_tbo(self.project_dir, data.get("tbo_id", ""))
            self._json_response(result)
        elif action == "update_status":
            result = _update_item_status(
                self.project_dir,
                data.get("file", ""),
                data.get("id_column", "ID"),
                data.get("id_value", ""),
                data.get("status", ""),
            )
            self._json_response(result)
        elif action == "refresh":
            write_dashboard(self.project_dir)
            self._json_response({"ok": True, "message": "Dashboard regenerated"})
        else:
            self._json_response({"ok": False, "error": f"Unknown action: {action}"})

    def _serve_dashboard(self) -> None:
        """Regenerate and serve the dashboard HTML."""
        path = write_dashboard(self.project_dir)
        html = path.read_text(encoding="utf-8")

        # Inject interactive controls (JavaScript for POST requests)
        controls_js = _build_controls_js()
        html = html.replace("</body>", f"{controls_js}</body>")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _json_response(self, data: dict) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format: str, *args) -> None:
        """Suppress default logging — use branded output."""
        pass


def _accept_tbo(project_dir: Path, tbo_id: str) -> dict:
    """Mark a TBO as DONE with today's date as actual completion."""
    from datetime import date

    docs_dir = project_dir / "claude_docs"
    obj_file = docs_dir / "_living_business_objectives.md"

    if not obj_file.exists():
        return {"ok": False, "error": "No _living_business_objectives.md found"}

    text = obj_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    updated = False

    for i, line in enumerate(lines):
        if f"| {tbo_id} " in line or f"| {tbo_id}|" in line:
            # Replace status with DONE and set actual date
            line = re.sub(
                r"\|\s*(ACCEPTANCE|IN_PROGRESS|OPEN|NOT_STARTED)\s*\|",
                "| DONE |",
                line,
            )
            # Set actual date (replace "—" in Actual column)
            today = str(date.today())
            line = re.sub(
                r"\|\s*\u2014\s*\|(\s*[^|]*\|)\s*$",
                f"| {today} |\\1",
                line,
            )
            lines[i] = line
            updated = True
            break

    if not updated:
        return {"ok": False, "error": f"TBO {tbo_id} not found"}

    obj_file.write_text("\n".join(lines), encoding="utf-8")
    write_dashboard(project_dir)
    return {"ok": True, "message": f"{tbo_id} accepted as DONE on {date.today()}"}


def _update_item_status(
    project_dir: Path, filename: str, id_col: str, id_val: str, new_status: str
) -> dict:
    """Update the status of any item in a markdown table."""
    ALLOWED_FILES = [
        "_project_tasks.md",
        "_project_stories.md",
        "_living_business_objectives.md",
        "_intake_features.md",
        "_intake_bugs.md",
        "_intake_gaps.md",
    ]

    if filename not in ALLOWED_FILES:
        return {"ok": False, "error": f"File not allowed: {filename}"}

    docs_dir = project_dir / "claude_docs"
    filepath = docs_dir / filename

    if not filepath.exists():
        return {"ok": False, "error": f"File not found: {filename}"}

    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()
    updated = False

    for i, line in enumerate(lines):
        if f"| {id_val} " in line or f"| {id_val}|" in line:
            # Find and replace the Status cell
            line = re.sub(
                r"\|\s*(DONE|IN_PROGRESS|OPEN|BLOCKED|ON_HOLD|ACCEPTANCE|NOT_STARTED|CLOSED|PENDING)\s*\|",
                f"| {new_status} |",
                line,
                count=1,
            )
            lines[i] = line
            updated = True
            break

    if not updated:
        return {"ok": False, "error": f"{id_val} not found in {filename}"}

    filepath.write_text("\n".join(lines), encoding="utf-8")
    write_dashboard(project_dir)
    return {"ok": True, "message": f"{id_val} updated to {new_status}"}


def _build_controls_js() -> str:
    """JavaScript for interactive dashboard controls."""
    return """
<script>
async function devleadAction(action, data) {
    try {
        const resp = await fetch('/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action, ...data})
        });
        const result = await resp.json();
        if (result.ok) {
            // Reload to show updated dashboard
            window.location.reload();
        } else {
            alert('DevLead: ' + (result.error || 'Unknown error'));
        }
    } catch (e) {
        alert('DevLead server not running. Start with: devlead serve');
    }
}

function acceptTBO(tboId) {
    if (confirm('Accept ' + tboId + ' as DONE? This marks the business outcome as delivered.')) {
        devleadAction('accept_tbo', {tbo_id: tboId});
    }
}

function updateStatus(file, idCol, idVal, newStatus) {
    devleadAction('update_status', {file, id_column: idCol, id_value: idVal, status: newStatus});
}
</script>
"""


def start_server(project_dir: Path, port: int = 8765) -> None:
    """Start the DevLead interactive dashboard server."""
    DevLeadHandler.project_dir = project_dir

    server = HTTPServer(("localhost", port), DevLeadHandler)
    print(ui.banner())
    print(ui.ok(f"Dashboard server running at http://localhost:{port}"))
    print(ui.info("Press Ctrl+C to stop"))
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(ui.info("Server stopped."))
        server.server_close()
