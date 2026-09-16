# V2.9 release checks

1. `python -m py_compile backend/app/main.py`
2. `pytest -q tests/test_v29_smoke.py` from the project root after installing backend requirements.
3. Manual accounting flow: create invoice -> post invoice -> create receipt voucher -> post voucher -> verify customer financial reconciliation.
4. Verify opening balance posting creates a balanced journal.
5. Verify fiscal-year close posts the net result and then blocks further postings in the closed period.
