import os
import click
from .utils import save_config, load_config, make_temp_tarfile
from .parser import load_spec_file
from .pipeline import Pipeline

@click.group()
def base():
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
        # Set YAGNA_APPKEY env for yagna.
        os.environ['YAGNA_APPKEY'] = config['api_key']
    except FileNotFoundError:
        # Check if YAGNA_APPKEY exists?
        if os.getenv('YAGNA_APPKEY') is not None:
            print("Please set the golem api key using set_api_key command or YAGNA_APPKEY env!")
            return
    # get absoloute path from context_dir
    context_dir = os.path.abspath(context_dir)
    print(f"Using context directory: {context_dir}")
    if context_dir == "" or not os.path.exists(context_dir):
        print("Please provide a valid context dir!")
        return
    spec = load_spec_file(context_dir)
    if spec is None:
        print("Couln't find a .golem-ci.yml file in context directory!")
    tar_fname = make_temp_tarfile(context_dir)
    
    # run pipeline for each steps
    pipeline = Pipeline(spec, tar_fname)



base.add_command(set_api_key)
base.add_command(up)
