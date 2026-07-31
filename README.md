# scala-doc-quality-kit

Markdown documentation link checker (Python) plus a GitHub Actions workflow.

## Local check

```bash
python scripts/check_doc_links.py
```

## Intentionally failing

Add a markdown link to a missing local path (for example `[missing](./nope.md)`).
The checker reports broken local paths and exits non-zero so CI fails.

Sample docs in `examples/sample-docs.md` only use good local links so CI passes.
