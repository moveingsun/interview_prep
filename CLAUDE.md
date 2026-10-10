# CLAUDE.md

This repo is Kurt Wang's interview-prep study guide for the **BCBSMA Sr. AI Engineer** role (hiring-manager round tentatively Fri Oct 16, 2026).

**Read [`HANDOFF.md`](HANDOFF.md) first.** It has the candidate background, the JD, what's done, verified facts, and the open items.

## Conventions for pages in `AI Engineer/`

- **File names:** `NN-Title-With-Hyphens.md`. Link between pages with relative paths (`[RAG](03-RAG.md)`). Link to stories with `13-Behavioral-Story-Bank.md#s1`; story anchors are `<a id="sN">` tags. `00-Index.md` must link to every page.
- **Page template:**
  - First line: `# NN · Title`.
  - Second line: `[← Index](00-Index.md) · **Manager-round priority:** … · **Read time:** …`.
  - Then a `> **Why this matters for this role:**` line, an optional `## Primer`, and `## Questions & answers`.
  - Each question is `### QN. <question>` followed by its tag.
  - Each answer has these parts:
    - **Say this first (~30 sec):** the spoken answer.
    - **If they dig deeper:** bullet points.
    - **Your angle:** links to the story IDs.
    - **Likely follow-ups:** what they might ask next.
  - The page ends with `## References`.
- **Tags:** `[P0]` likely in the manager round · `[P1]` likely in technical rounds · `[P2]` depth / bonus.
- **Story IDs:** S1–S14 come from the resume. M1, C1, F1, and P1 are for Kurt to fill in. Never invent Kurt's experience; use `[fill in: …]` for details only he knows. Coach honest framing of gaps, never exaggeration.
- **Accuracy:** content should be current as of Oct 2026. Verify product names and preview-vs-GA status on Microsoft Learn or docs.langchain.com before changing them.
- **Links:** verify every new external URL with `curl -sL -o /dev/null -w "%{http_code}" -A "Mozilla/5.0" --max-time 15 "<url>"`. Run `python3 tools/check_links.py . /tmp/urls.txt` after edits.
- **Phone-friendly:** Kurt reads this in the GitHub mobile app, so keep paragraphs short and avoid very wide tables or code lines.
- **Style:** plain English. Kurt is a non-native English speaker, so avoid idioms that are hard to say out loud.
