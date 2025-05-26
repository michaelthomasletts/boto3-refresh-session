#!/usr/bin/env python3

import requests
from jinja2 import Environment, FileSystemLoader


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
    package = "boto3-refresh-session"
    url = f"https://pepy.tech/api/v2/projects/{package}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    downloads = data.get("total_downloads", 0)
    downloads_abbr = abbreviate(downloads)

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("README.template.md")

    with open("README.md", "w") as f:
        f.write(template.render(downloads_abbr=downloads_abbr))


if __name__ == "__main__":
    run()
