# User Medical Data Record Schema

## Storage location

Store each user's data at:

- `/home/node/openclaw-shared/user_medical_data/<storage-folder>/medical_data.json`

Folder naming rule:
- Use a sanitized `telegram_user_id` when available.
- Otherwise use a sanitized `user_id`.

Canonical identifier rule:
- When `telegram_user_id` is available, persist that Telegram value as the record's `user_id`.
- `telegram_user_id` may also be stored explicitly for clarity/backward compatibility.

## Record structure

```json
{
  "schema_version": "1.0",
  "user_id": "123456789",
  "telegram_user_id": "123456789",
  "created_at": "2026-03-11T17:00:00Z",
  "updated_at": "2026-03-11T17:05:00Z",
  "basic_health_data": {
    "full_name": null,
    "preferred_name": null,
    "date_of_birth": null,
    "age": null,
    "sex": null,
    "gender": null,
    "blood_type": null,
    "height_cm": null,
    "weight_kg": null,
    "allergies": [],
    "chronic_conditions": [],
    "medications": [],
    "emergency_contact": null,
    "primary_physician": null,
    "notes": null
  },
  "symptom_health_timeline": [
    {
      "timestamp": "2026-03-11T17:04:00Z",
      "type": "symptom",
      "text": "Headache for the last 2 days",
      "source": "user_report",
      "status": "reported",
      "metadata": {}
    }
  ]
}
```

## Merge rules

- Create the record if it does not exist.
- Preserve existing content unless the new payload intentionally updates it.
- For scalar `basic_health_data` fields, overwrite only when the new value is non-empty.
- For list `basic_health_data` fields, merge unique values.
- For `symptom_health_timeline`, append non-empty new entries and skip exact duplicates.
- Keep timestamps in ISO-8601 UTC form when possible.
- Sort the timeline by timestamp after merging.

## Summary behavior

The companion summary script reads one user record and returns:
- record metadata (`user_id`, `telegram_user_id`, path, timestamps)
- only non-empty `basic_health_data` fields
- total timeline entry count
- symptom and measurement counts
- a recent slice of timeline entries

## Recommended timeline entry types

- `symptom`
- `health_note`
- `measurement`
- `diagnosis_history`
- `medication_update`

## Minimal payload example

```json
{
  "user_id": "123456789",
  "telegram_user_id": "123456789",
  "basic_health_data": {
    "age": 42,
    "blood_type": "O+"
  },
  "symptom_health_timeline": [
    {
      "timestamp": "2026-03-11T17:04:00Z",
      "type": "symptom",
      "text": "Low-grade fever since yesterday"
    }
  ]
}
```

## Execution hygiene

- Prefer stdin-based execution for updates so no temporary payload JSON file is written into the workspace.
- If a temporary payload file must be used, delete it immediately after the update completes.
