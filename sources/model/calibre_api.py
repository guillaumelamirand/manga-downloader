import sys
import subprocess 
import re
import logging
import calibre
from calibre.ebooks.metadata.book.base import Metadata
from calibre.srv.changes import books_added
from collections import defaultdict

class CalibreApi(object):
	_CHAPITER_REG_EX = 'Chapitre ([0-9]+)'
	_CHAPITER_ADDED_REG_EX = 'Added book ids: ([0-9]+)'
	read_client = None
	library_local_path = None
	logger = logging.getLogger()

	@staticmethod
	def init(library_local_path):
		CalibreApi.library_local_path = library_local_path
		CalibreApi.read_client = calibre.library.db(library_local_path).new_api

	@staticmethod
	def add_chapiter_to_serie(serie, series_index, title, cbz_path):
		CalibreApi.logger.debug('Adding new chapiter to serie with [serie=%s, series_index=%s, title=%s, cbz_path=%s]' % (serie, series_index, title, cbz_path))
		if serie.tags:
			if 'New' not in serie.tags:
				serie.tags = serie.tags + ('Nouveau',)
		else:
			serie.tags = ('Nouveau',)
		try:
			add_output = subprocess.check_output(["calibredb", \
				"add", \
				"--with-library", CalibreApi.library_local_path, \
				"--title", title, \
				"--series", serie.name, \
				"--series-index", str(series_index), \
				"--authors", ','.join(str(author) for author in serie.authors), \
				"--tags", ','.join(str(tag) for tag in serie.tags), \
				"--duplicates", \
				cbz_path], \
				stderr=subprocess.STDOUT)
			CalibreApi.logger.debug(add_output)

			added_id_search = re.search(CalibreApi._CHAPITER_ADDED_REG_EX, add_output)
			if (added_id_search):
				added_id = added_id_search.group(1)
				subprocess.check_output(["calibredb", \
					"set_metadata", \
					"--with-library", CalibreApi.library_local_path, \
					"--field", "publisher:%s" % serie.publisher,
					added_id], \
					stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError as e:
			CalibreApi.logger.exception('Unable to add chapitre to series with [serie=%s, series_index=%s, title=%s, cbz_path=%s]' % (serie.name, series_index, title, cbz_path))
			

	@staticmethod
	def get_serie(serie_name):		
		CalibreApi.logger.debug('Getting serie with [serie_name=%s]' % serie_name)
		book_ids= CalibreApi.read_client.search('series:%s' % serie_name)
		if len(book_ids) > 0:
			last_chapiter_id = sorted(book_ids)[-1]
			last_index =  CalibreApi._get_field(last_chapiter_id, 'series_index')		  
			try:
				title = CalibreApi._get_field(last_chapiter_id, 'title')
				last_chapiter = int(re.search(CalibreApi._CHAPITER_REG_EX, title).group(1))
			except AttributeError:
				last_chapiter = None # apply your error handling
			authors =  CalibreApi._get_field(last_chapiter_id, 'authors')		
			tags =  CalibreApi._get_field(last_chapiter_id, 'tags')	  
			publisher =  CalibreApi._get_field(last_chapiter_id, 'publisher')
			calibre_serie = CalibreSerie(serie_name, last_index, last_chapiter, authors, tags, publisher)
			CalibreApi.logger.debug('Calibre serie found with [%s]' % calibre_serie)
		else:			
			CalibreApi.logger.warn("No calibre serie found for %s" % serie_name)			
			input_authors = raw_input("Authors (separator ', '): ").decode(sys.stdin.encoding)
			if input_authors:
				authors = tuple(input_authors.split(', '))
			else:
				authors = ()
			input_tags = raw_input("Tags (separator ', '): ").decode(sys.stdin.encoding)
			if input_tags:
				tags = tuple(input_tags.split(', '))
			else:
				tags = ()
			publisher = raw_input("Publisher: ").decode(sys.stdin.encoding)

			calibre_serie = CalibreSerie(serie_name, 0, 0, authors, tags, publisher)
		return calibre_serie

	@staticmethod
	def _get_field(book_id, field_name):
		return CalibreApi.read_client.field_for(field_name, book_id)

class CalibreSerie(object):

	def __init__(self, name, last_index, last_chapiter, authors, tags, publisher):
		self.name = name
		self.last_index = last_index
		self.last_chapiter = last_chapiter
		self.authors = authors
		self.tags = tags
		self.publisher = publisher

	def get_next_index(self, index_increment, sub_index_max):
		next_index = self.last_index + index_increment
		if (sub_index_max):
			volume_index = int(self.last_index)
			volume_max = volume_index + sub_index_max
			if (next_index > volume_max):
				next_index = volume_index + 1 + index_increment
		CalibreApi.logger.debug('Next serie index built with [index_increment=%s, sub_index_max=%s, new_index=%s]' % (index_increment, sub_index_max, next_index))
		return next_index

	def get_chapiter_name(self, chapiter_index):
		return "Chapitre %s" % chapiter_index 

	def __repr__(self):
		return "%s(name=%r, last_index=%r, last_chapiter=%r, authors=%r, tags=%r, publisher=%r)" % (self.__class__.__name__, self.name, self.last_index, self.last_chapiter, self.authors, self.tags, self.publisher)
