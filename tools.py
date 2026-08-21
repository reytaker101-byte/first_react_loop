import json
import subprocess
import urllib.request
import urllib.error

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def check_service(service_name: str) -> dict:
    service_name = service_name.strip().lower()
    if not service_name:
        return {"found": False, "error": "Service name was empty."}

    code, stdout, stderr = run_command([
        "docker", "ps", "-a",
        "--filter", f"label=devops.service={service_name}",
        "--filter", "label=devops.role=nginx",
        "--format", "{{.ID}}"
    ])

    if code != 0:
        return {
            "found": False,
            "error": "Docker CLI is unavailable or Docker Desktop is not running.",
            "details": stderr
        }

    ids = [x for x in stdout.splitlines() if x]
    if not ids:
        return {
            "found": False,
            "service": service_name,
            "error": "No nginx container was found for this service."
        }

    container_id = ids[0]
    code, inspect_out, inspect_err = run_command(["docker", "inspect", container_id])
    if code != 0:
        return {"found": False, "service": service_name,
                "error": "Container was found but could not be inspected.",
                "details": inspect_err}

    data = json.loads(inspect_out)[0]
    state = data.get("State", {})
    labels = (data.get("Config", {}) or {}).get("Labels", {}) or {}

    running = bool(state.get("Running", False))
    health = (state.get("Health") or {}).get("Status", "not_configured")
    http_port = labels.get("devops.http_port")

    http_check = {"performed": False, "reachable": None, "url": None}
    if http_port:
        http_check.update({"performed": True, "url": f"http://127.0.0.1:{http_port}/"})
        if running:
            try:
                with urllib.request.urlopen(http_check["url"], timeout=3) as r:
                    http_check.update({"reachable": True, "http_status": r.status})
            except urllib.error.HTTPError as e:
                http_check.update({"reachable": True, "http_status": e.code})
            except Exception as e:
                http_check.update({"reachable": False, "error": str(e)})
        else:
            http_check.update({"reachable": False, "error": "Container is not running."})

    _, logs, _ = run_command(["docker", "logs", "--tail", "30", container_id])

    return {
        "found": True,
        "service": service_name,
        "container_name": data.get("Name", "").lstrip("/"),
        "container_id": container_id[:12],
        "status": state.get("Status", "unknown"),
        "running": running,
        "exit_code": state.get("ExitCode"),
        "restart_count": data.get("RestartCount", 0),
        "health": health,
        "http_check": http_check,
        "recent_logs": logs[-4000:] if logs else "(no recent logs)",
        "note": "These are observations; they do not automatically prove root cause."
    }
