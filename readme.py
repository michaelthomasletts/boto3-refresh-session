#!/usr/bin/env python3

import requests
from jinja2 import Environment, FileSystemLoader

package = "boto3-refresh-session"
url = f"https://pypistats.org/api/packages/{package}/overall"


def abbreviate(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    else:
        return str(n)


def run():
    with requests.Session() as session:
        # SSL verification deactivated due to issues with pypistats cert
        response = session.get(url=url, verify=False)
        response.raise_for_status()
        with_mirrors = 0
        without_mirrors = 0

        for daily_downloads in response.json()["data"]:
            if daily_downloads["category"] == "with_mirrors":
                with_mirrors += daily_downloads["downloads"]
            else:
                without_mirrors += daily_downloads["downloads"]

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("README.template.md")

    with open("README.md", "w") as f:
        f.write(
            template.render(
                with_mirrors=abbreviate(n=with_mirrors),
                without_mirrors=abbreviate(n=without_mirrors),
            ),
        )


if __name__ == "__main__":
    run()
