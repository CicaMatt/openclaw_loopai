---
name: dumb-calculator
description: Run a deliberately simple random addition generator that returns one random expression and its computed result. Use when the user explicitly asks to run a "dumb calculator".
---

# Dumb Calculator

Run a tiny calculator tool that generates a random addition and returns the computed result.

## Workflow

1. Confirm intent.
   - Use this skill only when the user explicitly asks for a dumb calculator run.

2. Run the tool.

```bash
python3 scripts/random_addition.py
```

3. Return the output.
   - The script returns JSON with:
     - `expression`: e.g. `"205 + 42"`
     - `result`: e.g. `247`

4. Present cleanly.
   - Show the expression and result in one short response.

## Notes

- This is intentionally random and intentionally simple.
- Do not ask the user for numbers unless they explicitly request a non-random calculator mode.
