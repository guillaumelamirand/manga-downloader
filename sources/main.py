
import logging
from setup import config
from models import Sources, Mangas, CalibreApi
from lib import calibre_api

# Load datas
Sources.load_items(config)
Mangas.load_items(config)

# Init calibre client
calibre_api = CalibreApi(config)

# Run
logger = logging.getLogger(__name__)
logger.info("Browse all mangas")

for manga in Mangas.get_all():
	logger.info("  -> %s on %s" %(manga.serie, manga.source))	
	calibre_serie = calibre_api.get_serie(manga.serie)
	source = Sources.get(manga.source)
	logger.info("      - Last chapiter in Calibre %s" % calibre_serie.last_chapiter )
	available_chapiters = source.get_available_chapiters(manga.id)
	new_chapiters = [chapiter for chapiter in available_chapiters if chapiter > calibre_serie.last_chapiter]
	if len(new_chapiters) == 0:
		logger.info("      - No new chapiters available")
	else:
		logger.info("      - New chapiters available %s" % new_chapiters)

	for chapiter in new_chapiters:
		logger.info("        ---- ")
		logger.info("        - Downloading chapiter %s" % chapiter)
		cbz_file = source.build_cbz(manga.id, chapiter)
		try:
			logger.info("        - Adding chapiter %s to Calibre" % chapiter)
			next_index = calibre_serie.get_next_index(manga.serie_index_increment, manga.serie_sub_index_max)
			calibre_chapiter_name = calibre_serie.get_chapiter_name(chapiter);
			calibre_api.add_chapiter_to_serie(calibre_serie, next_index, calibre_chapiter_name, cbz_file)
		finally:
			logger.debug("Remove cbz file '%s'" % cbz_file)	
			if os.path.exists(cbz_file):				
				try:
					os.remove(cbz_file)
				except Exception: 
					pass