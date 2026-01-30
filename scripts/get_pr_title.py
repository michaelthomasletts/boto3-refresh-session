# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Fetches the pull request title for the current commit."""

__all__ = ["main"]

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")

    if not token or not repo or not sha:
        return 0

    url = f"https://api.github.com/repos/{repo}/commits/{sha}/pulls"
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
    )

    try:
        with urlopen(request) as response:
            payload = response.read().decode("utf-8")
    except (HTTPError, URLError):
        return 0

    try:
        prs = json.loads(payload)
    except json.JSONDecodeError:
        return 0

    if prs:
        sys.stdout.write(prs[0].get("title", ""))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
