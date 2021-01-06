import click
from .utils import save_config, load_config, make_temp_tarfile
from .parser import load_spec_file
from .pipeline import Pipeline

@click.group()
def cli():
    pass

@click.command()
@click.argument('api_key')
def set_api_key(api_key):
    config = {"api_key": api_key}
    save_config(config)



@click.command()
@click.option('--tail', is_flag=True, help="Will print verbose messages.")
@click.argument('context_dir')
def up(tail, context_dir):
    config = {}
    try:
        config = load_config()
    except FileNotFoundError:
        print("Please set golem api key using set_api_key command!")
        return
    if context_dir == "" or not os.path.exists(context_dir):
        print("Please provide a valid context dir!")
        return
    spec = load_spec_file(context_dir)
    if spec is None:
        print("Couln't find a .golem-ci.yml file in context directory!")
    tar_fname = make_temp_tarfile(context_dir)

    # 1. send context to ipfs.
    
    # 2. run pipeline for each steps
    pipeline = Pipeline()



cli.add_command(set_api_key)
cli.add_command(up)
