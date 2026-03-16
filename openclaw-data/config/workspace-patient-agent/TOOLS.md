# TOOLS.md - LoopAI Patient Agent Tools Registry

---

## 1. Diagnostic & Screening Tools
Tools used to move from "vague symptom" to "structured data."

### `kidney-cancer-detector`
- **Description:** Analyzes kidney medical images (CT scans/MRIs) to identify potential malignancies using a specialized inference model.
- **Parameters:** `image_path` (string): The local path or URI of the medical image provided by the user..
- **When to use:** When a user provides a kidney scan for analysis.

---

## 2. Information & Research Tools
Tools used to provide evidence-based context.

### `pipeline-generator`
- **Description:** Generates a professional machine learning pipeline prototype based on a user's prompt. It interfaces with the AutoGen-model to provide a draft design covering data flow, training approach, and evaluation.
- **Parameters:** `prompt` (string): A detailed description of the ML pipeline prototype request..
- **When to use:** Use only when the user explicitly asks for an ML pipeline prototype to be defined or generated.

---

## 3. Patient Record & Retrieval Tools
Tools used to persist and retrieve longitudinal patient information.

### `user-medical-data-update`
- **Description:** Creates or updates a structured per-user medical record in `/home/node/openclaw-shared/user_medical_data` and can also summarize an existing user record.
- **Stored Data Structure:** One folder per user, containing `medical_data.json` with `basic_health_data` fields and a timestamped `symptom_health_timeline`.
- **When to use for logging:** Whenever the user shares new symptoms, health history, measurements, medications, allergies, or other medically relevant facts that should be preserved for later use.
- **When to use for retrieval:** Whenever the user asks for a summary, recap, overview, or review of their stored medical information or symptom history.
- **Logging Behavior:** Create the record if missing, merge basic profile fields carefully, append timestamped symptom/health entries, and avoid duplicating exact timeline events.
- **Summary Behavior:** Read the user file, return non-empty profile fields, counts of logged items, and a recent timeline summary.

---

## 4. General Utility Tools
Tools used for general-purpose tasks.

### `dumb-calculator`
- **Description:** Generates a single random addition expression (integers 0-999) and its computed result.
- **Parameters:** None.
- **When to use:** When the user explicitly requests to run a "dumb calculator".

---

Notes:
- When running tools, to do not mention any execution-related message, just answer the user as you have to, without previous repetitive sub-answers.
