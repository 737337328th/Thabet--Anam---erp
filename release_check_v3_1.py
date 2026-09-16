import pathlib, py_compile, zipfile
ROOT = pathlib.Path(__file__).resolve().parent
py_files = list(ROOT.rglob('*.py'))
for p in py_files:
    py_compile.compile(str(p), doraise=True)
required = [ROOT/'backend/app/main.py', ROOT/'backend/requirements.txt', ROOT/'docker-compose.yml']
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit('MISSING_CORE_FILES: ' + ', '.join(missing))
print(f'PASS: {len(py_files)} Python files compile successfully; core files present.')
