# Record-grounded SLM question template

Use this shape when turning retrieved patient records into a focused question for the SLM.

```text
Patient / record context:
- Patient id: <known or omitted>
- Main diagnoses / problems: <known facts only>
- Recent symptoms or concerns: <known facts only>
- Relevant labs / imaging / medications / visits: <known facts only>
- Important uncertainties or missing data: <if relevant>

Question for SLM:
<one clear question about the patient health data stored in records>
```

Guidance:
- Keep the final question focused and answerable.
- Base it only on retrieved records or clearly stated conversation context.
- Do not invent values, diagnoses, or history.
- Prefer one strong question over several weak ones.
- The calling agent should interpret the returned answer instead of relaying it blindly.