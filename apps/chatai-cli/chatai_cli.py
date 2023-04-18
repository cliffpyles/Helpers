#!/usr/bin/env python3

import glob
import requests
from urllib.parse import urljoin
import os
import sys
import click
import yaml
from pathlib import Path
import shutil

# Helper functions
def load_config_file(file_path):
    with open(file_path) as f:
        return yaml.safe_load(f)


def load_config():
    config_path = Path.home() / ".chatai" / "config.yaml"
    if config_path.exists():
        return load_config_file(config_path)
    return {}



# CLI commands
@click.group()
def cli():
    pass


@cli.command(help="Example command for the CLI based app.")
def example():
    config = load_config()
    click.echo("Command executed")


if __name__ == "__main__":
    cli()