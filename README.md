# Enrich SCADA

Reference-led React/TypeScript SCADA UI with a conservative FastAPI configuration contract.

## Run the frontend

```powershell
npm install
npm run dev
```

Use `npm run build` for a production bundle. The application opens in Demo mode. Live mode never presents demo values as live and reports unavailable acquisition data explicitly.

## Run the API

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn main:app --app-dir backend --reload --port 8000
```

The workbook endpoint stores source identity and returns a blocked draft until the approved workbook fixture and unresolved decoder rules are supplied. This is intentional: the specification explicitly forbids guessing those rules.

## Visual references

The nine original 1672×941 images extracted unchanged from the supplied DOCX are in [`design-references`](./design-references). Implementation status and engineering gates are tracked in [`docs/requirements-checklist.md`](./docs/requirements-checklist.md).
