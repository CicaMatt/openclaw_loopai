---
name: user-medical-data-update
description: Create or update structured per-user medical data records in /home/node/openclaw-shared/user_medical_data, and read them back as a concise summary. Use when a user shares symptoms, basic health profile facts, measurements, medication updates, or other patient-history details that should be persisted with timestamps and merged into an existing user record, or when the user asks to review/summarize their stored medical information. When Telegram sender context is available, store the record inside a folder named after the Telegram user ID.
---

# User Medical Data Update

Persist patient-reported medical context into one structured JSON file per user, and summarize it later when needed. Create the record when it does not exist, merge new basic profile facts carefully, append timestamped symptom or health-history entries without losing prior context, and read the file back into a usable overview.

## Update workflow

1. Identify the target user.
   - Use a stable identifier from the chat/session context when available.
   - If the session comes from Telegram and the Telegram sender ID is available, include it as `telegram_user_id`.
   - When `telegram_user_id` is present, treat it as the canonical stored `user_id` and use it for the storage folder name.
   - Reuse the same identifiers consistently so future updates hit the same record.

2. Separate the incoming information.
   - Put stable profile facts into `basic_health_data`.
   - Put dated or event-like statements into `symptom_health_timeline`.
   - If the user gives a symptom without an explicit time, use the current UTC timestamp and preserve the user wording in `text`.

3. Build the JSON payload.
   - Follow the schema in `references/schema.md`.
   - Include `user_id`.
   - When available from Telegram session metadata, also include `telegram_user_id`.
   - The update script will store the Telegram sender ID as the record's `user_id` and use it for the folder name when `telegram_user_id` is present.
   - Include only the fields you actually know.
   - Do not invent missing medical facts.
   - Prefer piping the JSON payload via stdin instead of writing a temporary file in the workspace.

4. Run the update script.

Preferred form, with no temporary payload file left behind:

```bash
cat <<'JSON' | python3 scripts/update_user_medical_data.py --payload-stdin
{
  "user_id": "123456789",
  "telegram_user_id": "123456789",
  "symptom_health_timeline": [
    {
      "timestamp": "2026-03-13T14:00:00Z",
      "type": "symptom",
      "text": "Headache since this morning"
    }
  ]
}
JSON
```

If a temporary payload file is unavoidable, create it outside the workspace when possible and always delete it immediately after use.

```bash
tmp_payload="$(mktemp)"
trap 'rm -f "$tmp_payload"' EXIT
cat > "$tmp_payload" <<'JSON'
{
  "user_id": "123456789"
}
JSON
python3 scripts/update_user_medical_data.py --payload-file "$tmp_payload"
rm -f "$tmp_payload"
trap - EXIT
```

5. Review the result.
   - Confirm the output path.
   - Confirm whether timeline entries were added.
   - If needed, read the updated JSON file and summarize what changed.

## Summary workflow

Use this when the user asks for a recap, summary, or overview of their stored medical information.

Run with the logical record id:

```bash
python3 scripts/summarize_user_medical_data.py --user-id <user-id>
```

Or run directly with the Telegram folder id:

```bash
python3 scripts/summarize_user_medical_data.py --telegram-user-id <telegram-user-id>
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
- When `telegram_user_id` is provided, store that value as `user_id` in the JSON record.
- Name the folder after `telegram_user_id` when provided; otherwise fall back to a sanitized `user_id`.
- Avoid leaving temporary payload JSON files in the agent workspace.
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
