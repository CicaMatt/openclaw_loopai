---
name: hrv-data
description: Simulate retrieval of HRV and smartwatch telemetry data by returning a fixed structured JSON payload from the bundled reference file and interpreting it clinically at a high level. Use when the user asks to fetch, read, inspect, summarize, or interpret HRV data, smartwatch telemetry, autonomic metrics, nocturnal vitals, stress metrics, sleep-derived cardiovascular signals, continuous heart-rate series, or wearable-derived blood pressure / heart-rate variability trends.
---

# HRV Data

Return the fixed telemetry payload from `references/dummy-watch-day-1.json` whenever this skill is used. Treat that file as the canonical simulated data source for this skill.

## Workflow

1. If the user asks to fetch or retrieve HRV / smartwatch telemetry data, read `references/dummy-watch-day-1.json` and return its JSON payload exactly.
2. If the user asks for interpretation, summarize the main findings from that same payload.
3. If the user asks for both, provide the JSON first, then a concise interpretation.
4. Present the output as simulated wearable telemetry, not as live or verified medical data.
5. Treat the output as a preliminary signal, not a diagnosis.

## Data Shape

The canonical payload now uses a continuous heart-rate series format:

- top-level key: `heart_rate_series`
- value: array of samples
- each sample contains:
  - `timestamp`: Unix timestamp in seconds
  - `bpm`: heart rate in beats per minute

## Interpretation Rules

When interpretation is requested:

- describe the series as a simulated wearable heart-rate time series;
- summarize overall heart-rate level, range, and visible variability;
- note whether the pattern looks relatively stable or highly erratic across the sampled window;
- avoid inventing unsupported fields such as blood pressure, sleep stages, stress score, RMSSD, or autonomic classifications unless they are explicitly present in the JSON;
- if HRV is discussed, clearly state that only a heart-rate series is available and that true HRV metrics would require beat-to-beat interval data or validated derived metrics.

## Response Style

Use plain language.

If the user wants a clinical-style summary, structure it as:
- What the telemetry shows
- What cannot be concluded from this file alone
- Important cautions
- Suggested next steps

Always make clear that:
- this is simulated smartwatch telemetry;
- wearable-derived physiological estimates have limitations;
- the result is a preliminary signal, not a confirmed diagnosis.
