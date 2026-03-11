---
name: user-medical-data-update
description: Create or update structured per-user medical data records in /home/node/openclaw-shared/user_medical_data, and read them back as a concise summary. Use when a user shares symptoms, basic health profile facts, measurements, medication updates, or other patient-history details that should be persisted with timestamps and merged into an existing user record, or when the user asks to review/summarize their stored medical information.
---

# User Medical Data Update

Persist patient-reported medical context into one structured JSON file per user, and summarize it later when needed. Create the record when it does not exist, merge new basic profile facts carefully, append timestamped symptom or health-history entries without losing prior context, and read the file back into a usable overview.

## Update workflow

1. Identify the target user.
   - Use a stable user identifier from the chat/session context when available.
   - Reuse the same identifier consistently so future updates hit the same folder.

2. Separate the incoming information.
   - Put stable profile facts into `basic_health_data`.
   - Put dated or event-like statements into `symptom_health_timeline`.
   - If the user gives a symptom without an explicit time, use the current UTC timestamp and preserve the user wording in `text`.

3. Build a JSON payload file.
   - Follow the schema in `references/schema.md`.
   - Include `user_id`.
   - Include only the fields you actually know.
   - Do not invent missing medical facts.

4. Run the update script.

```bash
python3 scripts/update_user_medical_data.py --payload-file /path/to/payload.json
```

5. Review the result.
   - Confirm the output path.
   - Confirm whether timeline entries were added.
   - If needed, read the updated JSON file and summarize what changed.

## Summary workflow

Use this when the user asks for a recap, summary, or overview of their stored medical information.

Run:

```bash
python3 scripts/summarize_user_medical_data.py --user-id <user-id>
```

Optional JSON output:

```bash
python3 scripts/summarize_user_medical_data.py --user-id <user-id> --format json
```

Optional limit for recent timeline items:

```bash
python3 scripts/summarize_user_medical_data.py --user-id <user-id> --recent-limit 5
```

## Field mapping guidance

### Put these in `basic_health_data`

Use for relatively stable patient facts:
- `full_name`
- `preferred_name`
- `date_of_birth`
- `age`
- `sex`
- `gender`
- `blood_type`
- `height_cm`
- `weight_kg`
- `allergies`
- `chronic_conditions`
- `medications`
- `emergency_contact`
- `primary_physician`
- `notes`

### Put these in `symptom_health_timeline`

Use for time-scoped or event-like information:
- new symptoms
- symptom progression
- measurements (blood pressure, temperature, glucose, weight changes)
- diagnoses the user reports
- medication starts/stops/changes
- procedures, hospital visits, injuries, follow-up notes

Each timeline item should include:
- `timestamp`
- `type`
- `text`

Optional fields:
- `source` (default: `user_report`)
- `status` (default: `reported`)
- `metadata` (extra structured detail)

## Merge and summary behavior

The bundled scripts apply the following rules:
- Create the user folder and `medical_data.json` if missing.
- Preserve prior data.
- Overwrite scalar basic fields only with non-empty new values.
- Merge unique values into list-based basic fields.
- Append non-empty timeline events.
- Skip exact duplicate timeline events.
- Sort the timeline after merging.
- Summaries include only non-empty basic fields, counts, and recent timeline entries.

## Resources

- Schema and examples: `references/schema.md`
- Update script: `scripts/update_user_medical_data.py`
- Summary script: `scripts/summarize_user_medical_data.py`
