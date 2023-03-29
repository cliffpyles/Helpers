# Helper functions
# ...

def get_template_variables(variables_str):
    if variables_str:
        return yaml.safe_load(variables_str)
    return {}

# CLI commands
# ...

@cli.command()
def init():
    blueprint_dir = Path('.blueprints')
    if not blueprint_dir.exists():
        blueprint_dir.mkdir()
        click.echo("Initialized empty blueprint directory at .blueprints")
    else:
        click.echo("Blueprint directory already exists at .blueprints")

@cli.command()
@click.argument('template_name')
@click.option('--variables', type=str, help="Template variables in YAML format.")
@click.option('--output', type=str, help="Output file path.")
def generate(template_name, variables, output):
    local_path = Path('.blueprints')
    global_path = Path.home() / ".blueprints"
    template_path = get_template_path(template_name, local_path, global_path)

    if not template_path:
        click.echo(f"Template '{template_name}' not found.")
        sys.exit(1)

    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    template = env.get_template(template_name)
    variables = get_template_variables(variables)

    rendered_content = template.render(**variables)

    if output:
        with open(output, 'w') as f:
            f.write(rendered_content)
        click.echo(f"Generated file '{output}' using template '{template_name}'")
    else:
        click.echo(rendered_content)

@cli.command()
@click.option('--local', is_flag=True, help="List local blueprints.")
def list_blueprints(local):
    if local:
        blueprint_path = Path('.blueprints')
        click.echo("Local blueprints:")
    else:
        blueprint_path = Path.home() / ".blueprints"
        click.echo("Global blueprints:")

    if blueprint_path.exists():
        blueprints = [entry.name for entry in blueprint_path.iterdir() if entry.is_file()]
        click.echo("\n".join(blueprints))
    else:
        click.echo("No blueprints found.")

@cli.command()
@click.argument('template_name')
@click.option('--local', is_flag=True, help="Create local blueprint.")
def create_blueprint(template_name, local):
    if local:
        blueprint_path = Path('.blueprints') / template_name
    else:
        blueprint_path = Path.home() / ".blueprints" / template_name

    if not blueprint_path.parent.exists():
        blueprint_path.parent.mkdir(parents=True)

    if blueprint_path.exists():
        click.echo(f"Blueprint '{template_name}' already exists.")
        sys.exit(1)

    with open(blueprint_path, 'w') as f:
        f.write("{{ variable_name|pipe_name }}")
    click.echo(f"Created new blueprint at {blueprint_path}")

@cli.command()
@click.argument('template_name')
@click.option('--variables', type=str, help="Template variables in YAML format.")
def create_project(template_name, variables):
    local_path = Path('.blueprints')
    global_path = Path.home() / ".blueprints"
    template_path = get_template_path(template_name, local_path, global_path)

    if not template_path:
        click.echo(f"Template '{template_name}' not found.")
        sys.exit(1)

    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    template = env.get_template(template_name)
    variables = get_template_variables(variables)

    rendered_content = template.render(**variables)

    project_name = variables.get('project_name', 'new_project')
    project_path = Path(project_name)
    project_path.mkdir(parents=True, exist_ok=True)

    with open(project_path / 'README.md', '
