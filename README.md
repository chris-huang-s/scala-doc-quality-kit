# scala-doc-quality-kit

Markdown documentation checks: local link integrity, fenced code language tags, single H1 per file, heading spacing, plus CI.

## Local checks

```bash
python scripts/check_doc_links.py
python scripts/check_code_fences.py
python scripts/check_single_h1.py
python scripts/check_heading_spacing.py
```

## Intentionally failing

Add a markdown link whose target is a missing local path, for example target `./nope.md`.
Write that as a real markdown link in a docs file (not inside backticks) and the checker will exit non-zero.

Sample docs in `examples/sample-docs.md` only use good local links and labeled fences so CI passes.
