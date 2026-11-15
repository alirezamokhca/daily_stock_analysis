#!/usr/bin/env python3
"""PaperDemoAgent trial, GitHub Actions version.

Same run as the local trial driver (run_demo.py), but the Gemini API key
comes from the environment (the repo secret GEMINI_API_KEY) instead of the
authd surrogate, which only exists on the local VM.

Paper: Tabiei & Zhang (2016), "Evaluation of Various Numerical Methods in
LS-DYNA for 3D Crack Propagation" (FEM/DEM/EFG/XFEM head-to-head).
Input is the extracted paper text in papers/tabiei-zhang-2016.txt.

Run in CI with GEMINI_API_KEY set; locally with the same env var:
    GEMINI_API_KEY=... python3 run_demo_ci.py
"""
import os
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_FILE = os.path.join(REPO_DIR, "papers", "tabiei-zhang-2016.txt")


def main() -> int:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("error: GEMINI_API_KEY is not set", file=sys.stderr)
        return 1
    os.environ["GOOGLE_API_KEY"] = key
    os.environ["GEMINI_API_KEY"] = key

    # The deprecated google.generativeai SDK defaults to gRPC; force REST
    # transport (plain HTTPS). Proven on the local VM, harmless on a runner.
    import google.generativeai as genai

    _orig_configure = genai.configure

    def _configure_with_rest(*args, **kwargs):
        kwargs.setdefault("transport", "rest")
        return _orig_configure(*args, **kwargs)

    genai.configure = _configure_with_rest

    from paper_demo_agent import PaperDemoAgent

    with open(TEXT_FILE, encoding="utf-8") as fh:
        text = fh.read()
    print(f"paper text: {len(text)} chars from {TEXT_FILE}", flush=True)

    # gemini-2.5-flash is retired for this key; gemini-3.8-flash is the
    # replacement the API itself names.
    agent = PaperDemoAgent(provider="gemini", model="gemini-3.8-flash")
    result = agent.run(
        source=text,
        demo_form="app",
        demo_subtype="gradio",
        max_iter=25,
        on_progress=print,
    )
    print("OUTPUT_DIR:", result.output_dir, flush=True)
    print("MAIN_FILE:", result.main_file, flush=True)
    print("RUN_COMMAND:", result.run_command, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
