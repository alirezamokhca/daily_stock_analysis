# PaperDemoAgent trial — Tabiei & Zhang (2016)

Builds an interactive Gradio demo from the paper **"Evaluation of Various
Numerical Methods in LS-DYNA for 3D Crack Propagation"** (Tabiei & Zhang,
2016 — FEM / DEM / EFG / XFEM head-to-head) using
[PaperDemoAgent](https://github.com/wshuai190/PaperDemoAgent) v0.4.0 with
Gemini (`gemini-3.8-flash`).

## How to run

Go to the **Actions** tab → "PaperDemoAgent — Tabiei & Zhang (2016)" →
**Run workflow**. The `GEMINI_API_KEY` repo secret already exists in this
repo (shared with the Daily Stock Analysis runs). When the run finishes,
download the `paper-demo-tabiei-zhang-2016` artifact — it contains the
generated Gradio app.

## Quota

The free Gemini tier allows 20 generate requests per day per model, shared
with the Daily Stock Analysis runs on the same key. Run this on a day the
daily runs will not compete (e.g. Saturday).

## Files

- `run_demo_ci.py` — CI driver (same run as the local trial, key from env)
- `papers/tabiei-zhang-2016.txt` — paper text extracted from the DYNAlook
  PDF (the live PDF could not be downloaded; this is the search-index
  extraction used for the local trial)
- `.github/workflows/paper-demo.yml` — the workflow
