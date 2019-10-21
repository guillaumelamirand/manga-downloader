# External import
import logging
import sh
import os
import calibre.library
import cfscrape

# Local import
from model.config import config
from model.calibre_api import CalibreApi
from model.sources import Sources
from model.mangas import Mangas

# Init logger
logger = logging.getLogger()
if (config['debug']):
	logger.setLevel(logging.DEBUG)
else:
	logger.setLevel(logging.INFO)

stream_formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] - %(module)-15s - %(message)s", "%Y-%m-%d %H:%M:%S")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

# Init calibre client from configuration
library_path = config['library_path']

if not os.path.exists(library_path + '/metadata.db'):
	logger.warn("Calibre metadata.db doesn't exist")
	raise RuntimeError('Calibre library doesn''t exists', library_path)

CalibreApi.init(library_path)

# Init sources from configuration
Sources._items = {source.id: source for source in config['sources']}
Sources._requestWrapper = cfscrape.create_scraper() ## this allows to by-pass cloudflare protection

# Init mangas from configuration
Mangas._items = {source.id: source for source in config['mangas']}
