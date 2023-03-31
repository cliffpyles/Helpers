#!/usr/bin/env python3

import requests
from urllib.parse import urljoin
import os
import sys
import click
import yaml
from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
from pipes import capitalize, upper, lower, kebab_case, snake_case, camel_case

# Helper functions
def load_config_file(file_path):
    with open(file_path) as f:
        return yaml.safe_load(f)


def get_template_path(template_name, local_path, global_path):
    config = load_config()
    local_path = Path(
        config.get("blueprints", {}).get("local_directory", ".blueprints")
    )
    global_path = Path(
        config.get("blueprints", {}).get("global_directory", "~/.blueprints")
    ).expanduser()

    local_template_path = local_path / template_name
    global_template_path = global_path / template_name

    if local_template_path.exists() and local_template_path.is_dir():
        return local_template_path
    elif global_template_path.exists() and global_template_path.is_dir():
        return global_template_path

    if not template_path:
        config = load_config()
        remote_repository = config.get("blueprints", {}).get("remote_repository")
        if remote_repository:
            blueprint_content = download_remote_blueprint(
                template_name, remote_repository
            )
            if blueprint_content:
                return blueprint_content
    return None


def get_template_variables(variables_str):
    if variables_str:
        return yaml.safe_load(variables_str)
    return {}


def get_environment_with_custom_pipes(template_path):
    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    env.filters["capitalize"] = capitalize
    env.filters["upper"] = upper
    env.filters["lower"] = lower
    env.filters["kebab_case"] = kebab_case
    env.filters["snake_case"] = snake_case
    env.filters["camel_case"] = camel_case
    return env


def copy_directory(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as e:
        click.echo(f"Error copying directory: {e}")
        sys.exit(1)


def load_config():
    config_path = Path.home() / ".blueprints" / "config.yaml"
    if config_path.exists():
        return load_config_file(config_path)
    return {}


def download_remote_blueprint(template_name, remote_repository):
    url = urljoin(remote_repository, template_name)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        click.echo(f"Error downloading remote blueprint: {e}")
        return None


def process_blueprint_directory(blueprint_dir, target_dir, variables, env):
    for root, _, files in os.walk(blueprint_dir):
        for file in files:
            source_path = Path(root) / file
            relative_path = source_path.relative_to(blueprint_dir)

            # Check if the file has dynamic content in the name and render it
            if "{{" in file and "}}" in file:
                file = Template(file).render(variables)

            target_path = target_dir / relative_path.parent / file
            target_path.parent.mkdir(parents=True, exist_ok=True)

            with open(source_path, "r") as source_file:
                content = source_file.read()
                rendered_content = env.from_string(content).render(variables)
                with open(target_path, "w") as target_file:
                    target_file.write(rendered_content)
            click.echo(f"Generated: {target_path}")


def generate_files_from_blueprint(template_path, variables, output):
    if isinstance(template_path, str):
        env = get_environment_with_custom_pipes(Path.cwd())
        template = env.from_string(template_path)
    else:
        env = get_environment_with_custom_pipes(template_path)
        template = env.get_template("")

    process_blueprint_directory(template_path, Path(output), variables, env)


# CLI commands
@click.group()
def cli():
    pass


@cli.command(help="Initialize a project for local blueprint support.")
def init():
    blueprint_dir = Path(".blueprints")
    if not blueprint_dir.exists():
        blueprint_dir.mkdir()
        click.echo("Initialized empty blueprint directory at .blueprints")
    else:
        click.echo("Blueprint directory already exists at .blueprints")


@cli.command(help="Generate a file from a blueprint template.")
@click.argument("template_name")
@click.option("--variables", type=str, help="Template variables in YAML format.")
@click.option("--output", type=str, help="Output file path.")
def generate(template_name, variables, output):
    local_path = Path(".blueprints")
    global_path = Path.home() / ".blueprints"
    template_path = get_template_path(template_name, local_path, global_path)
    if not template_path:
        click.echo(f"Blueprint '{template_name}' not found.")
        sys.exit(1)

    generate_files_from_blueprint(template_path, variables, output)


@cli.command(
    help="List available blueprints in the local and global blueprint directories."
)
@click.option("--local", is_flag=True, help="List local blueprints.")
def list_blueprints(local):
    if local:
        blueprint_path = Path(".blueprints")
        click.echo("Local blueprints:")
    else:
        blueprint_path = Path.home() / ".blueprints"
        click.echo("Global blueprints:")

    if blueprint_path.exists():
        blueprints = [
            entry.name for entry in blueprint_path.iterdir() if entry.is_dir()
        ]
        click.echo("\n".join(blueprints))
    else:
        click.echo("No blueprints found.")


@cli.command(help="Create a new blueprint in the local or global blueprint directory.")
@click.argument("template_name")
@click.option("--local", is_flag=True, help="Create local blueprint.")
def create_blueprint(template_name, local):
    if local:
        blueprint_path = Path(".blueprints") / template_name / "files" / f"{template_name}.j2"
    else:
        blueprint_path = Path.home() / ".blueprints" / template_name / "files" / f"{template_name}.j2"

    if not blueprint_path.parent.exists():
        blueprint_path.parent.mkdir(parents=True)

    if blueprint_path.exists():
        click.echo(f"Blueprint '{template_name}' already exists.")
        sys.exit(1)

    blueprint_path.write_text(f"{template_name} placeholder file")
    click.echo(f"Created new blueprint at {blueprint_path.parent}")


@cli.command(
    help="Copy an existing blueprint to a new blueprint in the local or global blueprint directory."
)
@click.argument("source_template_name")
@click.argument("destination_template_name")
@click.option("--local", is_flag=True, help="Copy to local blueprint directory.")
def copy_blueprint(source_template_name, destination_template_name, local):
    local_path = Path(".blueprints")
    global_path = Path.home() / ".blueprints"
    source_template_path = get_template_path(
        source_template_name, local_path, global_path
    )

    if not source_template_path:
        click.echo(f"Source template '{source_template_name}' not found.")
        sys.exit(1)

    destination_template_path = local_path if local else global_path
    destination_template_path /= destination_template_name

    if destination_template_path.exists():
        click.echo(
            f"Destination template '{destination_template_name}' already exists."
        )
        sys.exit(1)

    try:
        shutil.copy2(source_template_path, destination_template_path)
    except OSError as e:
        click.echo(f"Error copying blueprint: {e}")
        sys.exit(1)

    click.echo(
        f"Copied blueprint '{source_template_name}' to '{destination_template_name}'"
    )


@cli.command(
    help="Download a blueprint from a remote repository and save it to the local or global blueprint directory."
)
@click.argument("template_name")
@click.option(
    "--local", is_flag=True, help="Save the blueprint to the local blueprint directory."
)
def download_blueprint(template_name, local):
    config = load_config()
    remote_repository = config.get("blueprints", {}).get("remote_repository")
    if not remote_repository:
        click.echo("Remote repository not configured.")
        sys.exit(1)

    blueprint_content = download_remote_blueprint(template_name, remote_repository)
    if blueprint_content is None:
        click.echo(f"Blueprint '{template_name}' not found in remote repository.")
        sys.exit(1)

    destination_path = (
        Path(".blueprints" if local else config["blueprints"]["global_directory"])
        / template_name
    )
    with open(destination_path, "w") as f:
        f.write(blueprint_content)

    click.echo(f"Downloaded blueprint '{template_name}' to '{destination_path}'")


if __name__ == "__main__":
    cli()
