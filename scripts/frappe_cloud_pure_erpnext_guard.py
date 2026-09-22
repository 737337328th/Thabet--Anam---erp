from pathlib import Path

PACK = Path("frappe_cloud_ui_pack")

FORBIDDEN = (
    "Customs Clearance File",
    "thabet_anam_v4/",
    "Thabit Anam",
)

violations = []
for path in PACK.rglob("*"):
    if not path.is_file():
        continue
    if path.suffix.lower() not in {".md", ".csv", ".json", ".html"}:
        continue
    text = path.read_text(encoding="utf-8")
    for token in FORBIDDEN:
        if token in text:
            violations.append(f"{path}: forbidden V4/site assumption: {token}")

if violations:
    raise SystemExit("\n".join(violations))

print("Frappe Cloud pure ERPNext guard OK")
