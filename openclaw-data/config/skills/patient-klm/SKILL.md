---
name: patient-klm
description: Access and update a patient-specific knowledge store backed by a Patient KLM API that exposes EHR records, disease timelines, genomic profiles, and custom structured triples in SQLite. Use when a user asks to retrieve, inspect, summarize, add, or update patient knowledge base data; fetch patient context for agent personalization; view all triples for a patient; inspect the disease timeline; inspect genomics; create a new patient; add a visit; or add a custom triple. Default to patient_id `P-001` when the user asks for patient knowledge base access without specifying a patient. If the intended endpoint is unclear, ask a brief clarification question before writing data.
---

# Patient KLM

Use this skill to read from or write to the Patient KLM API at `http://looporchestra.sytes.net:8006`.

## Quick routing

Map the user request to exactly one endpoint when possible:

- **Get all patient triples / patient record / patient knowledge base** → `GET /patient/{patient_id}`
- **Get progression / disease course / timeline / labs over time / imaging over time** → `GET /patient/{patient_id}/timeline`
- **Get DNA / genomics / variants / genetic profile** → `GET /patient/{patient_id}/genomics`
- **Create a new patient** → `POST /patient`
- **Add a clinic visit / new appointment / follow-up encounter** → `POST /patient/{patient_id}/visit`
- **Add custom fact / family history / social history / risk factor / arbitrary triple** → `POST /triple`

If the user does not specify a patient for a read request, use `P-001`.

If the user asks for “access the knowledge base” but does not say *what* they want from it, ask a short clarification question such as:
- “Do you want the full patient record, the timeline, or the genomics profile?”

## Default behavior

- Prefer the helper script: `scripts/patient_klm_api.py`
- For read requests, return the API result and summarize it if the user appears to want interpretation.
- For write requests, confirm only when the request is ambiguous or materially incomplete. Do not add data that the user did not provide.
- Preserve user-provided field names and values exactly unless the API rejects them.

## Use the helper script

Run from the skill directory or pass the absolute path.

### Read patient data

```bash
python3 scripts/patient_klm_api.py get-patient --patient-id P-001
python3 scripts/patient_klm_api.py get-timeline --patient-id P-001
python3 scripts/patient_klm_api.py get-genomics --patient-id P-001
```

If `--patient-id` is omitted for read commands, the script defaults to `P-001`.

### Create or update patient data

Pass JSON inline or via a file.

```bash
python3 scripts/patient_klm_api.py add-patient --json '{"patient_id":"P-002","name":"John Smith"}'
python3 scripts/patient_klm_api.py add-visit --patient-id P-001 --json '{"visit_date":"2026-03-10","symptoms":["fatigue"]}'
python3 scripts/patient_klm_api.py add-triple --json '{"patient_id":"P-001","head":"P-001","relation":"has_risk_factor","tail":"smoking:20_pack_years"}'
```

Or:

```bash
python3 scripts/patient_klm_api.py add-patient --file payload.json
```

## Required data by operation

### `POST /patient`
Minimum required fields:
- `patient_id`
- `name`

Optional fields include demographics, baseline conditions, a first visit, and genomic variants.

### `POST /patient/{patient_id}/visit`
Require:
- `patient_id`
- visit payload JSON

Common visit fields:
- `visit_date`
- `symptoms`
- `vitals`
- `lab_results`
- `diagnosis_codes`
- `medications`
- `imaging`
- `clinical_notes`

### `POST /triple`
Require a JSON body containing at least the triple identity fields expected by the API, typically:
- `patient_id`
- `head`
- `relation`
- `tail`

Optional metadata may include:
- `confidence`
- `evidence_level`
- `source`
- `timestamp`

## Response handling

- If the API returns JSON, surface the key result cleanly.
- If a read response is large, summarize the main findings and offer the raw JSON on request.
- If a write succeeds, report what was added.
- If the API returns an error, quote the status and response body briefly so the user can correct the request.

## Files

- Helper script: `scripts/patient_klm_api.py`
- API reference: `references/api.md`
