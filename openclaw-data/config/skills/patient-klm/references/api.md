# Patient KLM API Reference

Base URL: `http://looporchestra.sytes.net:8006`
Swagger UI: `http://looporchestra.sytes.net:8006/docs`

## Endpoints

### `GET /patient/{patient_id}`
Return all triples for a patient as JSON.

Example:
```http
GET /patient/P-001
```

### `GET /patient/{patient_id}/timeline`
Return disease progression, diagnoses, lab values, and imaging findings ordered by date.

Example:
```http
GET /patient/P-001/timeline
```

### `GET /patient/{patient_id}/genomics`
Return DNA and genetic profile.

Example:
```http
GET /patient/P-001/genomics
```

### `POST /patient`
Add a new patient. Required: `patient_id`, `name`.

Minimal example:
```json
{
  "patient_id": "P-002",
  "name": "John Smith"
}
```

Full example:
```json
{
  "patient_id": "P-002",
  "name": "John Smith",
  "dob": "1975-06-20",
  "sex": "Male",
  "blood_type": "O+",
  "baseline_conditions": ["hypertension"],
  "visit_date": "2026-03-10",
  "symptoms": ["fatigue", "flank pain"],
  "lab_results": {"creatinine_mg_dl": 1.4, "egfr_ml_min": 65},
  "diagnosis_codes": ["ICD-10: N18.2"],
  "medications": ["Losartan 50mg daily"],
  "genetic_variants": [
    {
      "gene": "VHL",
      "variant_id": "rs123456",
      "clinical_significance": "pathogenic",
      "associated_condition": "Clear cell RCC"
    }
  ]
}
```

### `POST /patient/{patient_id}/visit`
Add a new EHR visit for an existing patient.

Example:
```json
{
  "visit_date": "2026-03-10",
  "symptoms": ["fatigue", "ankle swelling"],
  "vitals": {"blood_pressure": "145/90", "weight_kg": 78.5},
  "lab_results": {"creatinine_mg_dl": 1.8, "egfr_ml_min": 52},
  "diagnosis_codes": ["ICD-10: N18.3"],
  "medications": ["Amlodipine 5mg daily"],
  "imaging": {"type": "ultrasound", "findings": "Reduced kidney size bilateral"},
  "clinical_notes": "CKD progression noted"
}
```

### `POST /triple`
Add a custom triple directly.

Example:
```json
{
  "patient_id": "P-001",
  "head": "P-001",
  "relation": "has_risk_factor",
  "tail": "smoking:20_pack_years",
  "confidence": 0.90,
  "evidence_level": "II",
  "source": "patient_intake_form",
  "timestamp": "2026-03-10"
}
```

## Routing guidance

- “full patient record”, “patient KB”, “all triples” → `GET /patient/{patient_id}`
- “timeline”, “progression”, “how condition evolved” → `GET /patient/{patient_id}/timeline`
- “genomics”, “DNA”, “variants” → `GET /patient/{patient_id}/genomics`
- “create/add patient” → `POST /patient`
- “add visit/follow-up” → `POST /patient/{patient_id}/visit`
- “add custom fact/risk factor/family history/social history” → `POST /triple`

Default patient for unspecified read requests: `P-001`
