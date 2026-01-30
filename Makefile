PYTHON ?= python

BUMP := $(word 1,$(filter-out bump-version,$(MAKECMDGOALS)))

.PHONY: bump-version major minor patch get-pr-title

bump-version:
	@if [ -z "$(BUMP)" ]; then \
		echo "Usage: make bump-version {major|minor|patch}"; \
		exit 2; \
	fi
	$(PYTHON) scripts/bump_version.py "$(BUMP)"

major minor patch:
	@:

get-pr-title:
	uv run python scripts/get_pr_title.py
