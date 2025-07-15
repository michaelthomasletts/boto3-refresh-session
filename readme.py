#!/usr/bin/env python3

from os import getenv

from jinja2 import Environment, FileSystemLoader
from pepy_chart import PepyStats


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
    pepy = PepyStats(
        package="boto3-refresh-session",
        api_key=getenv("PEPY_API_KEY"),
        create_image=False,
    )
    total_downloads = pepy.total_downloads

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("README.template.md")

    with open("README.md", "w") as f:
        f.write(template.render(total_downloads=abbreviate(n=total_downloads)))


if __name__ == "__main__":
    run()
