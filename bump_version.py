import sys
from pathlib import Path

import tomlkit


def bump_version(version: str, part: str):
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


def main(part: str):
    path = Path("pyproject.toml")

    with path.open("r", encoding="utf-8") as f:
        pyproject = tomlkit.parse(f.read())

    current_version = str(pyproject["project"]["version"])
    new_version = bump_version(current_version, part)
    pyproject["project"]["version"] = new_version

    with path.open("w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(pyproject))

    print(f"Version bumped from {current_version} to {new_version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)

    main(sys.argv[1])
