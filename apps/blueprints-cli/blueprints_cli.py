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

    if local_template_path.exists():
        return local_template_path
    elif global_template_path.exists():
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
        click.echo(f"Template '{template_name}' not found.")
        sys.exit(1)

    if isinstance(template_path, str):
        template = Template(template_path)
    else:
        env = get_environment_with_custom_pipes(template_path.parent)
        template = env.get_template(template_name)

    variables = get_template_variables(variables)
    config = load_config()
    default_variables = config.get("blueprints", {}).get("default_variables", {})
    variables = {**default_variables, **variables}
    rendered_content = template.render(**variables)

    if output:
        with open(output, "w") as f:
            f.write(rendered_content)
        click.echo(f"Generated file '{output}' using template '{template_name}'")
    else:
        click.echo(rendered_content)


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
            entry.name for entry in blueprint_path.iterdir() if entry.is_file()
        ]
        click.echo("\n".join(blueprints))
    else:
        click.echo("No blueprints found.")


@cli.command(help="Create a new blueprint in the local or global blueprint directory.")
@click.argument("template_name")
@click.option("--local", is_flag=True, help="Create local blueprint.")
def create_blueprint(template_name, local):
    if local:
        blueprint_path = Path(".blueprints") / template_name
    else:
        blueprint_path = Path.home() / ".blueprints" / template_name

    if not blueprint_path.parent.exists():
        blueprint_path.parent.mkdir(parents=True)

    if blueprint_path.exists():
        click.echo(f"Blueprint '{template_name}' already exists.")
        sys.exit(1)

    with open(blueprint_path, "w") as f:
        f.write("{{ variable_name|pipe_name }}")
    click.echo(f"Created new blueprint at {blueprint_path}")


@cli.command(help="Create a project from a blueprint template.")
@click.argument("template_name")
@click.option("--variables", type=str, help="Template variables in YAML format.")
def create_project(template_name, variables):
    local_path = Path(".blueprints")
    global_path = Path.home() / ".blueprints"
    template_path = get_template_path(template_name, local_path, global_path)

    if not template_path:
        click.echo(f"Template '{template_name}' not found.")
        sys.exit(1)

    env = get_environment_with_custom_pipes(template_path.parent)
    try:
        if isinstance(template_path, str):
            template = Template(template_path)
        else:
            env = get_environment_with_custom_pipes(template_path.parent)
            template = env.get_template(template_name)
    except TemplateNotFound:
        click.echo(f"Template '{template_name}' not found.")
        sys.exit(1)

    variables = get_template_variables(variables)
    config = load_config()
    default_variables = config.get("projects", {}).get("default_variables", {})
    variables = {**default_variables, **variables}
    rendered_content = template.render(**variables)

    project_name = variables.get("project_name", "new_project")
    project_path = Path(project_name)

    try:
        project_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        click.echo(f"Error creating project directory: {e}")
        sys.exit(1)

    with open(project_path / "README.md", "w") as f:
        f.write(rendered_content)
    click.echo(f"Created new project '{project_name}' using template '{template_name}'")


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
