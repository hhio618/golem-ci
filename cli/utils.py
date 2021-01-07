
import os
import json
from appdirs import *
from . import NAME
import errno    
import tarfile
import tempfile
import hashlib
import shutil


def make_temp_tarfile(source_dir):
    tmpdir = tempfile.gettempdir()
    tmp_tarfile_name = os.path.join(tmpdir, os.path.basename(source_dir))
    shutil.make_archive(tmp_tarfile_name, 'zip', source_dir)
    return tmp_tarfile_name + ".zip"

def get_temp_log_file(step_name):
    fname = hashlib.md5(f"{step_name}".encode('utf-8')).hexdigest()
    tmpdir = tempfile.gettempdir()
    tmp_tarfile_name = os.path.join(tmpdir, f"{fname}.log")
    return tmp_tarfile_name

def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python ≥ 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def get_user_dir():
    return user_data_dir(NAME)

def get_config_file():
    dir = get_user_dir()
    return os.path.join(dir, "config.json")

def load_config():
    with open(get_config_file(), "r") as config_file:
        return json.load(config_file)

def save_config(configs):
    if not os.path.exists(get_user_dir()):
        mkdirs(get_user_dir())
    with open(get_config_file(), "w") as config_file:
        json.dump(configs, config_file)

