
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

_config_yml_full_path = os.path.join(_location, config_yml_path)

if not os.path.exists(_config_yml_full_path):
	raise RuntimeError('Configuration file doesn''t exist: %s', _config_yml_full_path)

with open(_config_yml_full_path, 'r') as configYml:
	config = _yaml.load(configYml)

##########################
## Init logger
logger = logging.getLogger()
logger.setLevel(config['log_level'])
formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] - %(module)-15s - %(message)s", "%Y-%m-%d %H:%M:%S")

## Init output handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)