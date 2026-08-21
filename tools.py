import json
import subprocess


def _run_docker(args):
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as exc:
        return {"exit_code": 1, "stdout": "", "stderr": str(exc)}


def list_containers():
    """List running and stopped Docker containers."""
    result = _run_docker(
        ["ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Image}}"]
    )
    if result["exit_code"] != 0:
        return json.dumps({"error": "Docker command failed", "details": result["stderr"]})

    containers = []
    for line in result["stdout"].splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            containers.append(
                {"name": parts[0], "status": parts[1], "image": parts[2]}
            )
    return json.dumps({"containers": containers}, indent=2)


def inspect_container(container_name: str):
    """Inspect one Docker container and return its state, health and restart information."""
    result = _run_docker(["inspect", container_name])
    if result["exit_code"] != 0:
        return json.dumps(
            {
                "status": "NOT_FOUND",
                "container": container_name,
                "message": "Container was not found. Do not guess its state.",
                "docker_error": result["stderr"],
            },
            indent=2,
        )

    try:
        data = json.loads(result["stdout"])[0]
        state = data.get("State", {})
        return json.dumps(
            {
                "status": "FOUND",
                "container": data.get("Name", "").lstrip("/"),
                "image": data.get("Config", {}).get("Image"),
                "state": state.get("Status"),
                "running": state.get("Running"),
                "exit_code": state.get("ExitCode"),
                "restart_count": data.get("RestartCount"),
                "health": state.get("Health", {}).get("Status", "not_configured"),
                "started_at": state.get("StartedAt"),
                "finished_at": state.get("FinishedAt"),
            },
            indent=2,
        )
    except (json.JSONDecodeError, IndexError) as exc:
        return json.dumps({"error": "Could not parse docker inspect output", "details": str(exc)})


def get_container_logs(container_name: str, tail: int = 50):
    """Read recent logs from a Docker container. Returns NOT_FOUND if the container does not exist."""
    result = _run_docker(["logs", "--tail", str(tail), container_name])
    if result["exit_code"] != 0:
        return json.dumps(
            {
                "status": "ERROR",
                "container": container_name,
                "message": "Could not read logs. Verify the container exists.",
                "docker_error": result["stderr"],
            },
            indent=2,
        )

    return json.dumps(
        {
            "status": "OK",
            "container": container_name,
            "tail": tail,
            "logs": result["stdout"][-12000:],
        },
        indent=2,
    )


AVAILABLE_FUNCTIONS = {
    "list_containers": list_containers,
    "inspect_container": inspect_container,
    "get_container_logs": get_container_logs,
}
