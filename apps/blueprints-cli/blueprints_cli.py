#!/usr/bin/env python3

import glob
import requests
import os
import sys
import click
import yaml
import shutil
import json
from urllib.parse import urljoin
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
from pipes import capitalize, upper, lower, kebab_case, snake_case, camel_case, pascal_case



# Helper functions
def load_config_file(file_path):
    with open(file_path) as f:
        return yaml.safe_load(f)


def get_local_blueprint_path(blueprint_name, local_path):
    config = load_config()
    local_path = Path(
        config.get("blueprints", {}).get("local_directory", ".blueprints")
    )
    local_blueprint_path = local_path / blueprint_name

    return local_blueprint_path


def get_global_blueprint_path(blueprint_name, global_path):
    config = load_config()
    global_path = Path(
        config.get("blueprints", {}).get("global_directory", "~/.blueprints")
    ).expanduser()
    global_blueprint_path = global_path / blueprint_name

    return global_blueprint_path


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


def copy_permissions(src_path, dest_path):
    """Copy permissions of src_path to dest_path"""
    mode = os.stat(src_path).st_mode
    os.chmod(dest_path, mode)


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


def process_blueprint_templates(templates, target_dir, env, variables, force):
    if not variables:
        variables = {}

    for template in templates:
        target_name = env.from_string(template.name.replace("___", "|")).render(variables)
        target_path = target_dir / target_name.strip(".j2")
        
        if target_path.exists() and not force:
            click.echo(f"Skipped: File '{target_path}' already exists. Use --force to overwrite.")
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)

            rendered_content = template.render(variables)

            with open(target_path, "w") as target_file:
                target_file.write(rendered_content)

            copy_permissions(template.filename, target_path)

            click.echo(f"Generated: {target_path}")


def process_variables(variables_str, metadata):
    variables = {}

    if variables_str:
        for variable_str in variables_str:
            if '==' in variable_str:
                key, value = variable_str.split('==', 1)
                variables[key] = value
            elif ':=' in variable_str:
                key, value = variable_str.split(':=', 1)
                try:
                    json_value = json.loads(value)
                except json.JSONDecodeError as e:
                    click.echo(f"Error parsing JSON for variable '{key}': {e}")
                    sys.exit(1)

                variables[key] = json_value

    variables.update(metadata)

    return variables


def generate_files_from_blueprint(blueprint_path, blueprint_instance_name, variables_str, output, force):
    blueprint_templates_dir = blueprint_path / "files"
    template_files = glob.glob("**/*.j2", root_dir=blueprint_templates_dir, recursive=True)
    env = get_environment_with_custom_pipes(blueprint_templates_dir)
    templates = [env.get_template(t) for t in template_files]
    metadata = {
        "blueprint_name": blueprint_path.name,
        "blueprint_instance_name": blueprint_instance_name
    }
    blueprint_variables = process_variables(variables_str, metadata)
    process_blueprint_templates(templates, Path(output), env, blueprint_variables, force)
    

def generate_command(blueprint_name, blueprint_instance_name, variables_str, output, force):
    local_path = Path(".blueprints")
    global_path = Path.home() / ".blueprints"
    blueprint_path = get_blueprint_path(blueprint_name, local_path, global_path)

    if not blueprint_path:
        click.echo(f"Blueprint '{blueprint_name}' not found.")
        sys.exit(1)

    generate_files_from_blueprint(blueprint_path, blueprint_instance_name, variables_str, output, force)


def list_blueprints_command(_global):
    if _global:
        blueprint_path = Path.home() / ".blueprints"
        click.echo("Global blueprints:")
    else:
        blueprint_path = Path(".blueprints")
        click.echo("Local blueprints:")

    if blueprint_path.exists():
        blueprints = [
            entry.name for entry in blueprint_path.iterdir() if entry.is_dir()
        ]
        click.echo("\n".join(blueprints))
    else:
        click.echo("No blueprints found.")


def create_blueprint_command(blueprint_name, **kwargs):
    if kwargs["global"]:
        blueprint_path = Path.home() / ".blueprints" / blueprint_name / "files" / f"{blueprint_name}.j2"
    else:
        blueprint_path = Path(".blueprints") / blueprint_name / "files" / f"{blueprint_name}.j2"

    if not blueprint_path.parent.exists():
        blueprint_path.parent.mkdir(parents=True)

    if blueprint_path.exists():
        click.echo(f"Blueprint '{blueprint_name}' already exists.")
        sys.exit(1)

    blueprint_path.write_text(f"{blueprint_name} placeholder file")
    click.echo(f"Created new blueprint at {blueprint_path.parent}")


def copy_blueprint_command(source_blueprint_name, destination_blueprint_name, global_src, global_dest):
    local_path = Path(".blueprints")
    global_path = Path.home() / ".blueprints"

    if(global_src):
        source_blueprint_path = get_global_blueprint_path(
            source_blueprint_name, global_path
        )
    else:
        source_blueprint_path = get_local_blueprint_path(
            source_blueprint_name, local_path
        )
    if not source_blueprint_path:
        click.echo(f"Source template '{source_blueprint_name}' not found.")
        sys.exit(1)


    if(global_dest):
        destination_blueprint_path = get_global_blueprint_path(
            destination_blueprint_name, global_path
        )
    else:
        destination_blueprint_path = get_local_blueprint_path(
            destination_blueprint_name, local_path
        )

    if destination_blueprint_path.exists():
        click.echo(
            f"Destination template '{destination_blueprint_name}' already exists."
        )
        sys.exit(1)

    try:
        shutil.copytree(source_blueprint_path, destination_blueprint_path)
    except OSError as e:
        click.echo(f"Error copying blueprint: {e}")
        sys.exit(1)

    if(global_src):
        source_message = f"using the global '{source_blueprint_name}' blueprint"
    else:
        source_message = f"using the local '{source_blueprint_name}' blueprint"
    
    if(global_dest):
        destination_message = f"'{destination_blueprint_name}' as a global blueprint"
    else:
        destination_message = f"'{destination_blueprint_name}' as a local blueprint"

    click.echo(
        f"Created {destination_message} {source_message}."
    )



# CLI commands
@click.group()
def cli():
    pass


@cli.command(help="Initialize a project for blueprint support.")
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
@click.option("--var", type=str, multiple=True, help="User-defined variables in 'name==value' or 'field:=json' format.")
@click.option("--output", type=str, help="Output file path.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing files.")
def generate(blueprint_name, blueprint_instance_name, var, output, force):
    generate_command(blueprint_name, blueprint_instance_name, var, output, force)


@cli.command(name="g", help="Generate files from a blueprint.", hidden=True)
@click.argument("blueprint_name")
@click.argument("blueprint_instance_name")
@click.option("--var", type=str, multiple=True, help="User-defined variables in 'name==value' or 'field:=json' format.")
@click.option("--output", type=str, help="Output file path.", default="./")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing files.")
def generate_alias(blueprint_name, blueprint_instance_name, var, output, force):
    generate_command(blueprint_name, blueprint_instance_name, var, output, force)


@cli.command(
    name="list",
    help="List available blueprints."
)
@click.option("-g", "--global", is_flag=True, help="List global blueprints.")
def list_blueprints(**kwargs):
    list_blueprints_command(kwargs["global"])


@cli.command(
    name="ls",
    help="List available blueprints.",
    hidden=True
)
@click.option("-g", "--global", is_flag=True, help="List global blueprints.")
def list_blueprints_alias(**kwargs):
    list_blueprints_command(kwargs["global"])


@cli.command(name="create", help="Create a new blueprint.")
@click.argument("blueprint_name")
@click.option("-g", "--global", is_flag=True, help="Create global blueprint.")
def create_blueprint(blueprint_name, **kwargs):
    create_blueprint_command(blueprint_name, **kwargs)


@cli.command(name="new", help="Create a new blueprint.", hidden=True)
@click.argument("blueprint_name")
@click.option("-g", "--global", is_flag=True, help="Create global blueprint.")
def create_blueprint_alias(blueprint_name, **kwargs):
    create_blueprint_command(blueprint_name, **kwargs)


@cli.command(
    name="copy",
    help="Create a copy of a blueprint"
)
@click.argument("source_blueprint_name")
@click.argument("destination_blueprint_name")
@click.option("-gs", "--global-src", is_flag=True, help="Copy a global blueprint.")
@click.option("-gd", "--global-dest", is_flag=True, help="Create a global blueprint.")
def copy_blueprint(source_blueprint_name, destination_blueprint_name, global_src, global_dest):
    copy_blueprint_command(source_blueprint_name, destination_blueprint_name, global_src, global_dest)


@cli.command(
    name="cp",
    help="Create a copy of a blueprint",
    hidden=True
)
@click.argument("source_blueprint_name")
@click.argument("destination_blueprint_name")
@click.option("-gs", "--global-src", is_flag=True, help="Copy a global blueprint.")
@click.option("-gd", "--global-dest", is_flag=True, help="Create a global blueprint.")
def copy_blueprint_alias(source_blueprint_name, destination_blueprint_name, global_src, global_dest):
    copy_blueprint_command(source_blueprint_name, destination_blueprint_name, global_src, global_dest)


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
