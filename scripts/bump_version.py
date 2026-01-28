# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Script for bumping project and package versions."""

import argparse
import os
import re
import sys
from pathlib import Path

import tomlkit

# default paths for version updates
DEFAULT_INIT_PATH = Path("boto3_refresh_session/__init__.py")
DEFAULT_PYPROJECT_PATH = Path("pyproject.toml")
BUMP_CHOICES = ("major", "minor", "patch")


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments for the bump operation.

    Returns
    -------
    argparse.Namespace
        The parsed arguments.
    """

    parser = argparse.ArgumentParser(
        description="Bump version in pyproject.toml and __init__.py."
    )
    parser.add_argument(
        "bump",
        choices=BUMP_CHOICES,
        help="Which part of the version to bump.",
    )
    parser.add_argument(
        "--init-path",
        default=str(DEFAULT_INIT_PATH),
        help="Path to the __init__.py file to update.",
    )
    parser.add_argument(
        "--pyproject-path",
        default=str(DEFAULT_PYPROJECT_PATH),
        help="Path to the pyproject.toml file to update.",
    )
    return parser.parse_args()


def bump_version(current_version: str, bump: str) -> str:
    """Bumps a semantic version string.

    Parameters
    ----------
    current_version : str
        Current version string in the form MAJOR.MINOR.PATCH.
    bump : str
        The version part to bump, e.g. "major".

    Returns
    -------
    str
        The bumped version string.
    """

    parts = current_version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(
            f"Expected MAJOR.MINOR.PATCH, got {current_version!r}."
        )

    major, minor, patch = (int(part) for part in parts)
    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1

    return f"{major}.{minor}.{patch}"


def update_pyproject_version(pyproject_path: Path, bump: str) -> str:
    """Updates the project version in pyproject.toml.

    Parameters
    ----------
    pyproject_path : Path
        Path to the pyproject.toml file.
    bump : str
        The version part to bump.

    Returns
    -------
    str
        The new version string.
    """

    text = pyproject_path.read_text(encoding="utf-8")
    data = tomlkit.parse(text)
    project = data.get("project")
    if project is None:
        raise ValueError("Missing [project] section in pyproject.toml.")
    if "version" not in project:
        raise ValueError("Missing version entry in [project].")

    current_version = project["version"]
    new_version = bump_version(str(current_version), bump)
    project["version"] = new_version
    new_text = tomlkit.dumps(data)

    if new_text != text:
        pyproject_path.write_text(new_text, encoding="utf-8")

    return new_version


def update_init_version(init_path: Path, version: str) -> bool:
    """Updates __version__ in the target __init__.py file.

    Parameters
    ----------
    init_path : Path
        Path to the __init__.py file to update.
    version : str
        Version string to set.

    Returns
    -------
    bool
        True if the file was changed.
    """

    text = init_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(?m)^(?P<prefix>__version__\s*=\s*)"
        r"(?P<quote>[\"\'])(?P<val>.*?)(?P=quote)\s*$"
    )

    # checking for an existing __version__ assignment
    match = pattern.search(text)
    if match is not None:
        replacement = (
            f"{match.group('prefix')}{match.group('quote')}"
            f"{version}{match.group('quote')}"
        )
        new_text = text[: match.start()] + replacement + text[match.end() :]
    else:
        # falling back to inserting after the last import, or appending
        import_pattern = re.compile(
            r"(?m)^(?:from\s+\S+\s+import\s+.+|import\s+\S+.*)$"
        )
        last_import = None
        for match in import_pattern.finditer(text):
            last_import = match
        if last_import is not None:
            insert_at = last_import.end()
            new_text = (
                text[:insert_at]
                + f'\n__version__ = "{version}"\n'
                + text[insert_at:]
            )
        else:
            new_text = text.rstrip() + f'\n\n__version__ = "{version}"\n'

    if new_text != text:
        init_path.write_text(new_text, encoding="utf-8")
        return True

    return False


def main() -> int:
    """Entrypoint for bumping versions."""

    args = parse_args()

    pyproject_path = Path(args.pyproject_path)
    if not pyproject_path.exists():
        print(
            f"{pyproject_path} not found; cannot update version.",
            file=sys.stderr,
        )
        return 1

    init_path = Path(args.init_path)
    if not init_path.exists():
        print(
            f"{init_path} not found; cannot update __version__.",
            file=sys.stderr,
        )
        return 1

    try:
        new_version = update_pyproject_version(pyproject_path, args.bump)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    update_init_version(init_path, new_version)

    # exporting the new version for GitHub Actions when available
    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a", encoding="utf-8") as env:
            env.write(f"NEW_VERSION={new_version}\n")

    print(f"Updated version to {new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
