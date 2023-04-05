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
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
from pipes import capitalize, upper, lower, kebab_case, snake_case, camel_case, pascal_case

# Helper functions
def load_config_file(file_path):
    with open(file_path) as f:
        return yaml.safe_load(f)


def get_blueprint_path(blueprint_name, local_path, global_path):
    config = load_config()
    local_path = Path(
        config.get("blueprints", {}).get("local_directory", ".blueprints")
    )
    global_path = Path(
        config.get("blueprints", {}).get("global_directory", "~/.blueprints")
    ).expanduser()

    local_blueprint_path = local_path / blueprint_name
    global_blueprint_path = global_path / blueprint_name

    if local_blueprint_path.exists() and local_blueprint_path.is_dir():
        return local_blueprint_path
    elif global_blueprint_path.exists() and global_blueprint_path.is_dir():
        return global_blueprint_path

    if not blueprint_path:
        config = load_config()
        remote_repository = config.get("blueprints", {}).get("remote_repository")
        if remote_repository:
            blueprint_content = download_remote_blueprint(
                blueprint_name, remote_repository
            )
            if blueprint_content:
                return blueprint_content
    return None


def get_blueprint_variables(variables_str, metadata):
    variables = {}

    if variables_str:
        variables = yaml.safe_load(variables_str)

    variables.update(metadata)

    return variables


def get_environment_with_custom_pipes(blueprint_path):
    env = Environment(loader=FileSystemLoader(str(blueprint_path)))
    env.filters["capitalize"] = capitalize
    env.filters["upper"] = upper
    env.filters["lower"] = lower
    env.filters["kebab_case"] = kebab_case
    env.filters["snake_case"] = snake_case
    env.filters["camel_case"] = camel_case
    env.filters["pascal_case"] = pascal_case

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


def download_remote_blueprint(blueprint_name, remote_repository):
    url = urljoin(remote_repository, blueprint_name)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        click.echo(f"Error downloading remote blueprint: {e}")
        return None


def process_blueprint_templates(templates, target_dir, env, variables):
    if not variables:
        variables = {}

    for template in templates:
        target_name = env.from_string(template.name.replace("___", "|")).render(variables)
        target_path = target_dir / target_name.strip(".j2")
        target_path.parent.mkdir(parents=True, exist_ok=True)

        rendered_content = template.render(variables)

        with open(target_path, "w") as target_file:
            target_file.write(rendered_content)

        click.echo(f"Generated: {target_path}")


def generate_files_from_blueprint(blueprint_path, blueprint_instance_name, variables, output):
    blueprint_templates_dir = blueprint_path / "files"
    template_files = glob.glob("**/*.j2", root_dir=blueprint_templates_dir, recursive=True)
    env = get_environment_with_custom_pipes(blueprint_templates_dir)
    templates = [env.get_template(t) for t in template_files]
    metadata = {
        "blueprint_name": blueprint_path.name,
        "blueprint_instance_name": blueprint_instance_name
    }
    blueprint_variables = get_blueprint_variables(variables, metadata)
    process_blueprint_templates(templates, Path(output), env, blueprint_variables)
    

def generate_command(blueprint_name, blueprint_instance_name, variables, output):
    local_path = Path(".blueprints")
    global_path = Path.home() / ".blueprints"
    blueprint_path = get_blueprint_path(blueprint_name, local_path, global_path)

    if not blueprint_path:
        click.echo(f"Blueprint '{blueprint_name}' not found.")
        sys.exit(1)

    generate_files_from_blueprint(blueprint_path, blueprint_instance_name, variables, output)


def list_blueprints_command(local):
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


@cli.command(name="generate", help="Generate files from a blueprint.")
@click.argument("blueprint_name")
@click.argument("blueprint_instance_name")
@click.option("--variables", type=str, help="Template variables in YAML format.")
@click.option("--output", type=str, help="Output file path.")
def generate(blueprint_name, blueprint_instance_name, variables, output):
    generate_command(blueprint_name, blueprint_instance_name, variables, output)


@cli.command(name="g", help="Generate files from a blueprint.", hidden=True)
@click.argument("blueprint_name")
@click.argument("blueprint_instance_name")
@click.option("--variables", type=str, help="Template variables in YAML format.")
@click.option("--output", type=str, help="Output file path.")
def generate_alias(blueprint_name, blueprint_instance_name, variables, output):
    generate_command(blueprint_name, blueprint_instance_name, variables, output)


@cli.command(
    name="list",
    help="List available blueprints in the local and global blueprint directories."
)
@click.option("--local", is_flag=True, help="List local blueprints.")
def list_blueprints(local):
    list_blueprints_command(local)


@cli.command(
    name="ls",
    help="List available blueprints in the local and global blueprint directories.",
    hidden=True
)
@click.option("--local", is_flag=True, help="List local blueprints.")
def list_blueprints_alias(local):
    list_blueprints_command(local)


@cli.command(help="Create a new blueprint in the local or global blueprint directory.")
@click.argument("blueprint_name")
@click.option("--local", is_flag=True, help="Create local blueprint.")
def create_blueprint(blueprint_name, local):
    if local:
        blueprint_path = Path(".blueprints") / blueprint_name / "files" / f"{blueprint_name}.j2"
    else:
        blueprint_path = Path.home() / ".blueprints" / blueprint_name / "files" / f"{blueprint_name}.j2"

    if not blueprint_path.parent.exists():
        blueprint_path.parent.mkdir(parents=True)

    if blueprint_path.exists():
        click.echo(f"Blueprint '{blueprint_name}' already exists.")
        sys.exit(1)

    blueprint_path.write_text(f"{blueprint_name} placeholder file")
    click.echo(f"Created new blueprint at {blueprint_path.parent}")


@cli.command(
    help="Copy an existing blueprint to a new blueprint in the local or global blueprint directory."
)
@click.argument("source_blueprint_name")
@click.argument("destination_blueprint_name")
@click.option("--local", is_flag=True, help="Copy to local blueprint directory.")
def copy_blueprint(source_blueprint_name, destination_blueprint_name, local):
    local_path = Path(".blueprints")
    global_path = Path.home() / ".blueprints"
    source_blueprint_path = get_blueprint_path(
        source_blueprint_name, local_path, global_path
    )

    if not source_blueprint_path:
        click.echo(f"Source template '{source_blueprint_name}' not found.")
        sys.exit(1)

    destination_blueprint_path = local_path if local else global_path
    destination_blueprint_path /= destination_blueprint_name

    if destination_blueprint_path.exists():
        click.echo(
            f"Destination template '{destination_blueprint_name}' already exists."
        )
        sys.exit(1)

    try:
        shutil.copy2(source_blueprint_path, destination_blueprint_path)
    except OSError as e:
        click.echo(f"Error copying blueprint: {e}")
        sys.exit(1)

    click.echo(
        f"Copied blueprint '{source_blueprint_name}' to '{destination_blueprint_name}'"
    )


@cli.command(
    help="Download a blueprint from a remote repository and save it to the local or global blueprint directory."
)
@click.argument("blueprint_name")
@click.option(
    "--local", is_flag=True, help="Save the blueprint to the local blueprint directory."
)
def download_blueprint(blueprint_name, local):
    config = load_config()
    remote_repository = config.get("blueprints", {}).get("remote_repository")
    if not remote_repository:
        click.echo("Remote repository not configured.")
        sys.exit(1)

    blueprint_content = download_remote_blueprint(blueprint_name, remote_repository)
    if blueprint_content is None:
        click.echo(f"Blueprint '{blueprint_name}' not found in remote repository.")
        sys.exit(1)

    destination_path = (
        Path(".blueprints" if local else config["blueprints"]["global_directory"])
        / blueprint_name
    )
    with open(destination_path, "w") as f:
        f.write(blueprint_content)

    click.echo(f"Downloaded blueprint '{blueprint_name}' to '{destination_path}'")


if __name__ == "__main__":
    cli()
