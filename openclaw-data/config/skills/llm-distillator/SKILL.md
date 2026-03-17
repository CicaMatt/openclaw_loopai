---
name: llm-distillator
description: Distill health-related conversation context plus diagnostic tool output into a clear, comprehensive patient-facing answer using a Hugging Face-hosted Llama 70B model. Use when the agent needs to (1) extract clinically relevant context from the current conversation, including symptoms, history, red flags, timelines, and other useful health details, (2) combine that context with the output of a diagnosis or screening tool, and (3) produce a concise but complete explanation that is easy for a user to understand.
---

# Llm Distillator

## Overview

Use this skill to synthesize two inputs into one final explanation: the health-relevant conversation context and the output of a diagnostic tool. The bundled script calls a Hugging Face chat-completions endpoint with a Llama 70B instruction model and returns a clean, user-facing summary.

## Workflow

1. Extract only the health-relevant parts of the current conversation.
2. Gather the diagnostic or screening tool output exactly as produced.
3. Run `scripts/distill_health_response.py` with both inputs.
4. Review the generated answer for safety, uncertainty, and emergency red flags before sending it.

## Extract conversation context

Include only information that helps clinical interpretation or next-step guidance:

- Current symptoms and severity
- Onset, duration, and timeline
- Relevant negatives and positives
- Prior diagnoses, tests, medications, allergies, and risk factors if present
- The user’s explicit concerns or goals
- Contradictions between subjective report and tool output

Do not pass unrelated small talk or irrelevant project chatter.

## Prepare tool output

Preserve the diagnostic result as faithfully as possible. Include:

- The exact tool name if known
- Raw output or structured result
- Confidence, classification, or score if present
- Any caveats or limitations already reported by the tool

## Run the script

Basic usage:

```bash
python3 scripts/distill_health_response.py \
  --context-file /tmp/health_context.txt \
  --diagnosis-file /tmp/diagnosis_output.txt
```

Direct text usage:

```bash
python3 scripts/distill_health_response.py \
  --context "Patient reports right flank pain for 2 weeks, intermittent blood in urine, no fever." \
  --diagnosis "Kidney scan classifier output: suspicious lesion detected, confidence 0.81."
```

Optional flags:

- `--model`: override the default Hugging Face model
- `--temperature`: default `0.2`
- `--max-tokens`: default `700`
- `--print-prompt`: print the assembled prompt instead of calling the API
- `--output-file`: save the final distilled answer to a file

## Output requirements

The desired output should:

- Be clear and readable for a non-expert
- Combine conversation context and tool output into one narrative
- Distinguish findings from uncertainty
- Avoid overstating certainty
- Mention urgent escalation when the combined picture suggests red flags
- End with practical next-step guidance when appropriate

## Safety rules

Always review the generated output before using it.

- Do not treat the LLM answer as an independent diagnosis.
- Preserve uncertainty if the source tool was uncertain.
- If emergency symptoms are present, prioritize urgent evaluation language.
- If the conversation context conflicts with the diagnostic output, say so plainly.
- Do not invent lab values, timelines, or findings that were not present in the inputs.

## Bundled resources

- `scripts/distill_health_response.py`: calls the Hugging Face chat-completions API with a Llama 70B model.
- `references/prompt-contract.md`: defines the expected input and output contract for consistent distillation.
