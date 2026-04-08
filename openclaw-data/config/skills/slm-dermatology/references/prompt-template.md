# Dermatology SLM question template

Use this shape when turning retrieved patient records, lesion descriptions, rash history, or already-established image context into one focused dermatology question for the SLM.

```text
Patient / dermatology context:
- Patient id: <known or omitted>
- Main skin concern: <known facts only>
- Lesion / rash description: <known morphology, distribution, duration, symptoms>
- Relevant history / treatments / triggers / images: <known facts only>
- Important uncertainties or missing data: <if relevant>

Question for SLM:
<one clear dermatology question grounded in the available context>
```

Guidance:
- Keep the final question focused and answerable.
- Base it only on retrieved records or clearly stated conversation context.
- Do not invent morphology, diagnoses, timing, or response-to-treatment details.
- Prefer one strong dermatology question over several weak ones.
- The calling agent should interpret the returned answer instead of relaying it blindly.
