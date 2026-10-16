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

Set `DATABASE_URL` before starting the API, for example:

```powershell
$env:DATABASE_URL = "postgresql://enrich_user:password@localhost:5432/enrich_scada"
```

Saving from CONFIG inserts an immutable `DRAFT` row into PostgreSQL. The newest draft is restored by `GET /api/v1/config/drafts/latest`; generated inverter ports are recalculated from the saved count and base port during restore. If the API or database is unavailable, the UI reports the error and never shows a success message.

The CONFIG page supports multiple independent plants. `GET /api/v1/plants` supplies the plant selector, `GET /api/v1/plants/{plant_id}/configuration` restores the selected plant, and every save inserts a new DRAFT snapshot linked to that plant. Adding or editing one plant does not replace another plant's records.

## Visual references

The nine original 1672×941 images extracted unchanged from the supplied DOCX are in [`design-references`](./design-references). Implementation status and engineering gates are tracked in [`docs/requirements-checklist.md`](./docs/requirements-checklist.md).
