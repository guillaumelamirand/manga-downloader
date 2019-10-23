
import logging
import os
from ruamel.yaml import YAML
import sys
from models import Manga, Source

##########################
## Init configuration
_location = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

_yaml = YAML()
_yaml.register_class(Manga)
_yaml.register_class(Source)

config_yml_path = './config.yml'
if len(sys.argv) == 2:
	config_yml_path = sys.argv[1]

with open(os.path.join(_location, config_yml_path), 'r') as configYml:
	config = _yaml.load(configYml)

##########################
logging.basicConfig(level=config['log_level'], format="%(asctime)s [%(levelname)-8s] - %(module)-15s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
