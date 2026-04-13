# Specialty SLM question template

Use this shape when turning retrieved patient records, kidney history, blood-pressure context, cardiovascular findings, or already-established renal/cardiac imaging context into one focused nephrology/cardiology/hypertension question for the SLM.

```text
Patient / specialty context:
- Patient id: <known or omitted>
- Main kidney / blood-pressure / cardiovascular concern: <known facts only>
- Relevant symptoms / findings / imaging context: <known facts only>
- Relevant history / medications / labs / studies: <known facts only>
- Important uncertainties or missing data: <if relevant>

Question for SLM:
<one clear specialty question grounded in the available context>
```

Guidance:
- Keep the final question focused and answerable.
- Base it only on retrieved records or clearly stated conversation context.
- Do not invent diagnoses, morphology, test results, timing, or treatment response.
- Prefer one strong specialty question over several weak ones.
- The calling agent should interpret the returned answer instead of relaying it blindly.
