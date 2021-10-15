
import logging
from setup import config
from models import Sources, Mangas, CalibreApi, Notification, HomeAssistant

# Load datas
Sources.load_items(config)
Mangas.load_items(config)

# Init calibre client
calibre_api = CalibreApi(config)

# Init home assistant client
notifications = []
home_assistant = HomeAssistant(config)


# Run
logger = logging.getLogger(__name__)
logger.info("Browse all mangas")

# Start processing mangas
for manga in Mangas.get_all():
	try:
		logger.info("  -> %s on %s" %(manga.serie, manga.source))
		calibre_serie = calibre_api.get_serie(manga.serie)
		source = Sources.get(manga.source)
		logger.info("      - Last chapiter in Calibre %s" % calibre_serie.last_chapiter )

		available_chapiters = source.get_available_chapiters(manga.id)
		new_chapiters = [chapiter for chapiter in available_chapiters if chapiter not in getattr(manga, 'chapiter_ignored', []) and chapiter > calibre_serie.last_chapiter]
		if len(new_chapiters) == 0:
			logger.info("      - No new chapiters available")
		else:
			logger.info("      - New chapiters available %s" % new_chapiters)

		for chapiter in new_chapiters:
			cbz_file = None
			try:
				logger.info("        ---- Chapiter %s" % chapiter)
				logger.info("           - Build")
				cbz_file = source.build_chapiter(manga.id, chapiter)

				logger.info("           - Add to Calibre")
				next_index = calibre_serie.get_next_index(manga.serie_index_increment, manga.serie_sub_index_max)
				calibre_chapiter_name = calibre_serie.get_chapiter_name(chapiter);
				calibre_api.add_chapiter_to_serie(calibre_serie, next_index, calibre_chapiter_name, cbz_file)
				calibre_serie.last_index = next_index
				notifications.append(Notification(manga.serie, chapiter, True))
			except Exception as error:
				logger.error("           - Error: %s" % error)
				notifications.append(Notification(manga.serie, chapiter, False))
				break
			finally:
				logger.debug("Remove cbz file '%s'" % cbz_file)
				try:
					if os.path.exists(cbz_file):
						os.remove(cbz_file)
				except Exception:
					pass
	except Exception as error:
		logger.error("           - Error: %s" % error)
		notifications.append(Notification(manga.serie, "unknown", False))

#Send notification
if len(notifications) > 0:
	home_assistant.notify(notifications)
