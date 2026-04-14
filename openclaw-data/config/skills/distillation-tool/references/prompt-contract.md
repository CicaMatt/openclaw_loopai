# Prompt contract

## Purpose

Combine health-relevant conversation context with diagnostic-tool output and produce a comprehensive, user-facing explanation.

## Input sections

The script sends two structured sections:

1. `Conversation context`
   - symptoms
   - duration and timeline
   - risk factors
   - relevant negatives
   - user concerns

2. `Diagnostic tool output`
   - tool name
   - raw or structured result
   - confidence / caveats / classification

## Desired output shape

Prefer this structure when the content supports it:

1. Brief overall impression
2. What the conversation adds
3. What the diagnostic tool suggests
4. Uncertainty or limitations
5. Recommended next step / urgency

## Style

- Plain language
- Calm and medically cautious
- No invented facts
- No hidden chain-of-thought
- No absolute certainty unless explicitly present in the inputs
