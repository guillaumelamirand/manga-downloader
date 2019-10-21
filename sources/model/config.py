from ruamel.yaml import YAML
import os
import sys
from model.mangas import Manga, Mangas
from model.sources import Sources, Source

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

_yaml = YAML()

_yaml.register_class(Manga)
_yaml.register_class(Source)

config_yml_path = '../config.yml'
if len(sys.argv) == 2:
	config_yml_path = sys.argv[1]

with open(os.path.join(__location__, config_yml_path), 'r') as configYml:
	config = _yaml.load(configYml)
