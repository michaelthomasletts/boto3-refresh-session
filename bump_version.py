import argparse
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

    path = Path("pyproject.toml")

    # reading current version from pyproject.toml
    pyproject = path.read_text(encoding="utf-8")
    pyproject = tomlkit.parse(pyproject)

    # bumping version
    new_version = bump_version(
        current_version := str(pyproject["project"]["version"]), part
    )
    pyproject["project"]["version"] = new_version

    # writing bumped version to pyproject.toml
    path.write_text(tomlkit.dumps(pyproject), encoding="utf-8")

    print(f"Version bumped from {current_version} to {new_version}")


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
