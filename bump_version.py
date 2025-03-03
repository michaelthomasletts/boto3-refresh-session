import argparse
import re
import sys
from pathlib import Path

import tomlkit

HELP_MSG = """Which part of the version to bump (default: patch).
Example: python bump_version.py minor"""


def bump_version(version: str, part: str):
    """Bumps version according to the part parameter."""

    major, minor, patch = map(int, version.split("."))

    if part == "major":
        major += 1
        minor = patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        print("Invalid part. Use 'major', 'minor', or 'patch'.")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def run(part: str):
    """Runs the bump_version method using the part parameter."""

    # reading current version from pyproject.toml
    path = Path("pyproject.toml")
    pyproject = path.read_text(encoding="utf-8")
    pyproject = tomlkit.parse(pyproject)

    # bumping version
    new_version = bump_version(
        current_version := str(pyproject["project"]["version"]), part
    )
    pyproject["project"]["version"] = new_version

    # writing bumped version to pyproject.toml
    path.write_text(tomlkit.dumps(pyproject), encoding="utf-8")

    print(
        f"Version bumped from {current_version} to {new_version} in {path.name}"
    )

    # writing bumped version to __init__.py
    path = Path("boto3_refresh_session/__init__.py")
    path.write_text(re.sub(r"\d+\.\d+\.\d+", new_version, path.read_text()))

    print(
        f"Version bumped from {current_version} to {new_version} in {path.name}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bump the project version.")
    parser.add_argument(
        "part",
        choices=["major", "minor", "patch"],
        default="patch",
        nargs="?",
        help=HELP_MSG,
    )
    args = parser.parse_args()
    run(part=args.part)
