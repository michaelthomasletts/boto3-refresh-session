# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

from pathlib import Path

import tomlkit

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "boto3_refresh_session"


def _load_pyproject():
    path = ROOT / "pyproject.toml"
    return tomlkit.parse(path.read_text(encoding="utf-8"))


def _normalize_entries(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def _entry_includes_package(entry: str) -> bool:
    normalized = entry.strip().rstrip("/")
    if normalized in {"", ".", "./"}:
        return True
    if normalized == PACKAGE:
        return True
    return normalized.startswith(f"{PACKAGE}/")


def _entry_excludes_package_root(entry: str) -> bool:
    normalized = entry.strip().rstrip("/")
    if normalized == PACKAGE:
        return True
    return normalized in {f"{PACKAGE}/*", f"{PACKAGE}/**"}


def test_wheel_includes_package():
    package_init = ROOT / PACKAGE / "__init__.py"
    assert package_init.is_file(), f"Missing package init: {package_init}"

    pyproject = _load_pyproject()
    build = pyproject.get("tool", {}).get("hatch", {}).get("build", {})
    wheel = build.get("targets", {}).get("wheel", {})

    only_include = _normalize_entries(
        wheel.get("only-include") or wheel.get("only_include")
    )
    if only_include:
        assert any(_entry_includes_package(entry) for entry in only_include), (
            "Wheel only-include does not include boto3_refresh_session"
        )

    packages = _normalize_entries(
        wheel.get("packages") or build.get("packages")
    )
    if packages:
        assert any(
            entry == PACKAGE or entry.startswith(f"{PACKAGE}.")
            for entry in packages
        ), "Wheel packages do not include boto3_refresh_session"

    excludes = _normalize_entries(build.get("exclude")) + _normalize_entries(
        wheel.get("exclude")
    )
    assert not any(
        _entry_excludes_package_root(entry) for entry in excludes
    ), "Wheel excludes remove boto3_refresh_session"
