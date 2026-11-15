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
# Condensed paper text: the full 18,427-char extraction timed out the first
# Gemini call three times (600 s read timeout in Phase 1). The short version
# keeps the title, abstract, all four methods, key formulas and all result
# numbers, at ~12k chars, so the research call finishes in time.
TEXT_FILE = os.path.join(REPO_DIR, "papers", "tabiei-zhang-2016-short.txt")


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

    # The first Gemini call timed out three times at the SDK's default
    # 600 s read timeout. Give slow generations up to 1200 s instead.
    # PaperDemoAgent calls model.generate_content internally, so wrap it
    # to inject the longer timeout when the caller did not set one.
    _orig_generate = genai.GenerativeModel.generate_content

    def _generate_with_timeout(self, *args, **kwargs):
        opts = dict(kwargs.get("request_options") or {})
        opts.setdefault("timeout", 1200)
        kwargs["request_options"] = opts
        return _orig_generate(self, *args, **kwargs)

    genai.GenerativeModel.generate_content = _generate_with_timeout

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
