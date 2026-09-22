from pathlib import Path
import re

ROOT = Path("thabet_anam_v4")

FORBIDDEN_SUBSTRINGS = (
    ".submit(",
    ".cancel(",
    "make_gl_entries",
    'new_doc("Journal Entry")',
    "new_doc('Journal Entry')",
    'delete_doc("GL Entry"',
    "delete_doc('GL Entry'",
    'db.set_value("GL Entry"',
    "db.set_value('GL Entry'",
)

quote = chr(96)
FORBIDDEN_REGEX = (
    re.compile(rf"(?is)\\b(?:insert|update|delete)\\s+(?:into\\s+|from\\s+)?{quote}?tabGL Entry{quote}?"),
    re.compile(rf"(?is)\\b(?:insert|update|delete)\\s+(?:into\\s+|from\\s+)?{quote}?tabJournal Entry{quote}?"),
)

violations = []
for path in ROOT.rglob("*.py"):
    source = path.read_text(encoding="utf-8")

    for token in FORBIDDEN_SUBSTRINGS:
        if token in source:
            violations.append(f"{path}: forbidden financial automation token: {token}")

    for pattern in FORBIDDEN_REGEX:
        if pattern.search(source):
            violations.append(
                f"{path}: forbidden direct SQL write to accounting tables: {pattern.pattern}"
            )

if violations:
    raise SystemExit("\\n".join(violations))

print("Financial safety guard OK")
