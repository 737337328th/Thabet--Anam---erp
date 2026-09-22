from pathlib import Path

FORBIDDEN = (
    ".submit(",
    "make_gl_entries",
    'new_doc("Journal Entry")',
    "new_doc('Journal Entry')",
)

violations = []
for path in Path("thabet_anam_v4").rglob("*.py"):
    text = path.read_text(encoding="utf-8")
    for token in FORBIDDEN:
        if token in text:
            violations.append(f"{path}: forbidden financial automation token: {token}")

if violations:
    raise SystemExit("\n".join(violations))

print("Financial safety guard OK")
