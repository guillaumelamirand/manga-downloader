import calibre
from calibre.ebooks.metadata.book.base import Metadata
from calibre.srv.changes import books_added
from collections import defaultdict
import logging
import os
import re
import sys
import subprocess 

_CHAPITER_REG_EX = 'Chapitre ([0-9]+)'
_CHAPITER_ADDED_REG_EX = 'Added book ids: ([0-9]+)'
_LOGGER = logging.getLogger(__name__)

class CalibreApi(object):
	
	def __init__(self, config):
		
		# Init calibre client from configuration
		self.library_path = config['calibre']['library']
		if not os.path.exists(self.library_path + '/metadata.db'):
			raise RuntimeError('Calibre library doesn''t exists.', library_path)

		self.api_client = calibre.library.db(self.library_path).new_api

	def add_chapiter_to_serie(self, serie, series_index, title, cbz_path):
		_LOGGER.debug('Adding new chapiter to serie with [serie=%s, series_index=%s, title=%s, cbz_path=%s]' % (serie, series_index, title, cbz_path))
		if serie.tags:
			if 'New' not in serie.tags:
				serie.tags = serie.tags + ('Nouveau',)
		else:
			serie.tags = ('Nouveau',)
		try:
			add_output = subprocess.check_output(["calibredb", \
				"add", \
				"--with-library", self.library_path, \
				"--title", title, \
				"--series", serie.name, \
				"--series-index", str(series_index), \
				"--authors", ','.join(str(author) for author in serie.authors), \
				"--tags", ','.join(str(tag) for tag in serie.tags), \
				"--duplicates", \
				cbz_path], \
				stderr=subprocess.STDOUT)
			_LOGGER.debug(add_output)

			added_id_search = re.search(_CHAPITER_ADDED_REG_EX, add_output)
			if (added_id_search):
				added_id = added_id_search.group(1)
				subprocess.check_output(["calibredb", \
					"set_metadata", \
					"--with-library", self.library_path, \
					"--field", "publisher:%s" % serie.publisher,
					added_id], \
					stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError as e:
			_LOGGER.exception('Unable to add chapitre to series with [serie=%s, series_index=%s, title=%s, cbz_path=%s]' % (serie.name, series_index, title, cbz_path))
			
	def get_serie(self, serie_name):		
		_LOGGER.debug('Getting serie with [serie_name=%s]' % serie_name)
		book_ids= self.api_client.search('series:%s' % serie_name)
		if len(book_ids) > 0:
			last_chapiter_id = sorted(book_ids)[-1]
			last_index =  self._get_field(last_chapiter_id, 'series_index')		  
			try:
				title = self._get_field(last_chapiter_id, 'title')
				last_chapiter = int(re.search(_CHAPITER_REG_EX, title).group(1))
			except AttributeError:
				last_chapiter = None # apply your error handling
			authors =  self._get_field(last_chapiter_id, 'authors')		
			tags =  self._get_field(last_chapiter_id, 'tags')	  
			publisher =  self._get_field(last_chapiter_id, 'publisher')
			calibre_serie = CalibreSerie(serie_name, last_index, last_chapiter, authors, tags, publisher)
			_LOGGER.debug('Calibre serie found with [%s]' % calibre_serie)
		else:			
			_LOGGER.warn("No calibre serie found for %s" % serie_name)			
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

	def _get_field(self, book_id, field_name):
		return self.api_client.field_for(field_name, book_id)

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
		_LOGGER.debug('Next serie index built with [index_increment=%s, sub_index_max=%s, new_index=%s]' % (index_increment, sub_index_max, next_index))
		return next_index

	def get_chapiter_name(self, chapiter_index):
		return "Chapitre %s" % chapiter_index 

	def __repr__(self):
		return "%s(name=%r, last_index=%r, last_chapiter=%r, authors=%r, tags=%r, publisher=%r)" % (self.__class__.__name__, self.name, self.last_index, self.last_chapiter, self.authors, self.tags, self.publisher)
