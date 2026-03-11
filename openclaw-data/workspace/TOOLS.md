# TOOLS.md - LoopBot Tools Registry

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

## 3. General Utility Tools
Tools used for general-purpose tasks.

### `dumb-calculator`
- **Description:** Generates a single random addition expression (integers 0-999) and its computed result.
- **Parameters:** None.
- **When to use:** When the user explicitly requests to run a "dumb calculator".

---