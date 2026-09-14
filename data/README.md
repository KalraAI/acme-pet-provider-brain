# Synthetic fixture

Run `python3 generate.py` from the repository root to deterministically create `data/claims.csv` with 9,283 fully synthetic claim rows. Then run `python3 analyze.py` and `python3 verify.py`.

The generated CSV is intentionally not hand-maintained. The generator is the source of truth for the reproducible fixture.
