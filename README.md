# scala-doc-quality-kit

Markdown documentation checks: local link integrity and fenced code language tags, plus CI.

## Local checks

```bash
python scripts/check_doc_links.py
python scripts/check_code_fences.py
```

## Intentionally failing

Add a markdown link to a missing local path (for example `[missing](./nope.md)`).
The link checker reports broken local paths and exits non-zero so CI fails.

Sample docs in `examples/sample-docs.md` only use good local links and labeled fences so CI passes.
