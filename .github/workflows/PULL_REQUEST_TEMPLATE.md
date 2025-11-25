## Summary

<!-- Short description of the change (1–3 sentences). -->

## Changes

- ...

## How to run / verify locally

```bash
# (Optional) create & activate virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install / update dependencies
pip install -r requirements.txt

# Lint (same as CI)
ruff check pages autotests
black --check pages autotests

# Run fast UI smoke suite
HEADLESS=1 pytest autotests -m smoke -v
```

If your change affects deeper Azercell login flows and you have access
to a real test phone number, you can additionally run:

```bash
export AZERCELL_PHONE="5XXXXXXXXX"  # do NOT commit real numbers
HEADLESS=1 pytest autotests -m "smoke or regression" -v
```

## Checklist

- [ ] Tests added/updated where necessary
- [ ] `ruff` and `black` pass locally
- [ ] Documentation updated (README / docs / test cases / traceability)
      if behaviour or flows changed