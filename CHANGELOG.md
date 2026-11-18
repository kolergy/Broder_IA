# Changelog

## v0.1.1 — 2026-11-16

### Fixed
- **deps:** declare matplotlib for the DXF inspection tool, archive the pinned install list, type the tests
  requirements_verrouillees.txt moved to archive/; README row removed; install guide section 6 now reproduces the prototype versions with uv sync --locked from uv.lock, Ink/Stitch dependencies still from inkstitch/requirements.txt. matplotlib declared (needed by ezdxf's drawing add-on in tools/inspect_sources.py, which could not run without it), unpinned, register entry DEP_008. prototype/tests/test_chaine.py: type annotations on every test and helper, unused mode renamed _mode, nested with merged; ruff and mypy --strict clean. pyproject.toml: [tool.mypy] with mypy_path prototype, untyped calls into the untyped chaine package allowed, shapely stubs ignored. Tests: 18 passed, 1 skipped (Ink/Stitch not configured). uv audit: no known vulnerabilities in 36 packages.

