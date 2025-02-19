import sys

import toml


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
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

    current_version = pyproject["tool"]["poetry"]["version"]
    new_version = bump_version(current_version, part)
    pyproject["tool"]["poetry"]["version"] = new_version

    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f)

    print(f"Version bumped from {current_version} to {new_version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)

    main(sys.argv[1])
