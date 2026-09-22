from pathlib import Path
import tomllib

REQUIRED_PATHS = (
    Path("pyproject.toml"),
    Path("thabet_anam_v4/hooks.py"),
    Path("thabet_anam_v4/install.py"),
    Path("thabet_anam_v4/api.py"),
    Path("thabet_anam_v4/thabet_anam_v4/doctype/customs_clearance_file/customs_clearance_file.json"),
    Path("deploy/free_local/docker_zero_cost.sh"),
    Path("deploy/free_local/backup_local.sh"),
    Path("deploy/free_local/health_check.sh"),
    Path("deploy/free_local/prepare_ubuntu.sh"),
    Path("deploy/free_local/START_WINDOWS.ps1"),
)

missing = [str(p) for p in REQUIRED_PATHS if not p.exists()]
if missing:
    raise SystemExit("Missing required repository paths:\n" + "\n".join(missing))

with open("pyproject.toml", "rb") as handle:
    project = tomllib.load(handle)

if project["project"]["name"] != "thabet_anam_v4":
    raise SystemExit("pyproject project name must be thabet_anam_v4")

deps = project.get("tool", {}).get("bench", {}).get("frappe-dependencies", {})
if "frappe" not in deps or "erpnext" not in deps:
    raise SystemExit("Frappe and ERPNext v16 dependencies must be declared")

hooks = Path("thabet_anam_v4/hooks.py").read_text(encoding="utf-8")
if 'app_name = "thabet_anam_v4"' not in hooks:
    raise SystemExit("hooks.py app_name mismatch")
if 'required_apps = ["erpnext"]' not in hooks:
    raise SystemExit("ERPNext must remain a required app")

for secret_path in (
    Path("deploy/oracle/.secrets"),
    Path("deploy/free_local/.secrets"),
    Path("deploy/free_local/.runtime/.secrets"),
):
    if secret_path.exists():
        raise SystemExit(f"Secret file must not be committed: {secret_path}")

print("Repository integrity check OK")
