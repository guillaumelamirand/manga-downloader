# External import
import cfscrape
import requests
import re
import tempfile
import logging
import shutil
import os
import zipfile

_LOGGER = logging.getLogger(__name__)
_EXT_REGEX = '.*\.(.*)'

class Sources(object):	
	_items = None

	@staticmethod
	def load_items(config):		
		Sources._items = {source.id: source for source in config['sources']}

	@staticmethod
	def get_items():
		return Mangas._items.iteritems()

	@staticmethod
	def get_all():
		return Sources._items.values()

	@staticmethod
	def get(id):
		return Sources._items[id]

class Source(object):

	_request_wrapper = cfscrape.create_scraper()
	
	def __init__(self, id, base_url, manga_page, chapiter_page, chapiter_regex, page_regex, image_regex): 
		self.id = id
		self.base_url = base_url
		self.manga_page = manga_page
		self.chapiter_page = chapiter_page		
		self.chapiter_regex = chapiter_regex
		self.page_regex = page_regex
		self.image_regex = image_regex
		_LOGGER.debug("Create Source: " + self)

	def get_available_chapiters(self, manga_id):
		_LOGGER.debug("Getting available chapiters for [manga_id=%s]" % manga_id)
		if not self._exists(manga_id):
			raise ValueError("No manga found for %s on %s" % (manga_id, self.id))

		manga_url = self._build_url(self.manga_page % manga_id)
		response = Source._request_wrapper.get(manga_url)
		return sorted(set(map(int, re.findall(self.chapiter_regex % manga_id, response.text))))

	def build_chapiter(self, manga_id, chapiter):
		_LOGGER.debug("Building chapiter for [manga_id=%s, chapiter=%s]" % (manga_id, chapiter))	
		if not self._exists(manga_id):
			raise ValueError("No manga found for %s on %s" % (manga_id, self.id))
		chapiter_dir = tempfile.mkdtemp()
		try:
			self._download_chapiter(manga_id, chapiter, chapiter_dir)
			cbz = self._zip_dir_to_cbz(chapiter_dir)
			_LOGGER.debug("Cbz build '%s'" % cbz)	
		finally:
			_LOGGER.debug("Remove working directory '%s'" % chapiter_dir)	
			if os.path.exists(chapiter_dir):			
				try:
					shutil.rmtree(chapiter_dir)
				except Exception: 
					pass
		return cbz

	def _exists(self, manga_id):
		manga_url = self._build_url(self.manga_page % manga_id);
		response = Source._request_wrapper.get(manga_url)
		return response.status_code == requests.codes.ok

	def _download_chapiter(self, manga_id, chapiter, target):
		_LOGGER.debug("Downloading chapiter [manga_id=%s, chapiter=%s, target=%s]" % (manga_id, chapiter, target))
		chapiter_url = self._build_url(self.chapiter_page % (manga_id, chapiter))
		response = Source._request_wrapper.get(chapiter_url, allow_redirects=True)
		try:
			pages_url = self._sorted_nicely(set(re.findall(self.page_regex, response.text)))
			for idx, page_url in enumerate(pages_url):
				self._download_page(idx + 1 , page_url, target)
		except AttributeError:
			images_url = self._sorted_nicely(set(re.findall(self.image_regex, response.text)))
			for idx, image_url in enumerate(images_url):
				self._download_image(idx + 1 , image_url, target)


	def _download_page(self, page_idx, page_url, target): 
		_LOGGER.debug("Downloading page [page_idx=%s, page_url=%s, target=%s]" % (page_idx, page_url, target))
		response = Source._request_wrapper.get(page_url)
		image_url = re.search(self.image_regex, response.text).group(1)
		self._download_image(page_idx, image_url, target)		

	def _download_image(self, page_idx, image_url, target): 
		_LOGGER.debug("Downloading image [page_idx=%s, image_url=%s, target=%s]" % (page_idx, image_url, target))
		ext = re.search(_EXT_REGEX, image_url).group(1)
		with open('%s/%03d.%s' % (target, page_idx, ext), 'wb') as handle:
			response = Source._request_wrapper.get(image_url, stream=True)

			if not response.ok:
				_LOGGER.error("Error when downloading page [page_idx=%s, page_url=%s]" % (page_idx, page_url))
				raise ValueError("Unable to downaload page with [page_idx=%s, page_url=%s, target=%s]" % (page_idx, page_url, target))

			for block in response.iter_content(1024):
				if not block:
					_LOGGER.error("Error when downloading page [page_idx=%s, page_url=%s]" % (page_idx, page_url))
					break

				handle.write(block)

	def _build_url(self, path): 
		return self.base_url + path

	def _sorted_nicely(selft, iterable):
	    """ Sorts the given iterable in the way that is expected.
	 
	    Required arguments:
	    l -- The iterable to be sorted.
	 
	    """
	    convert = lambda text: int(text) if text.isdigit() else text
	    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
	    return sorted(iterable, key = alphanum_key)

	def _zip_dir_to_cbz(self, directory):
		# The root directory within the ZIP file.
		cbz_file = directory + '.cbz'
		outZipFile = zipfile.ZipFile(cbz_file, 'w', zipfile.ZIP_DEFLATED)

		for dirpath, dirnames, filenames in os.walk(directory):
			for filename in filenames:
				# Write the file named filename to the archive,
				# giving it the archive name 'arcname'.
				filepath   = os.path.join(dirpath, filename)
				arcname = os.path.relpath(filepath, directory)

				outZipFile.write(filepath, arcname)

		outZipFile.close()
		return cbz_file

	def __repr__(self):
		return "%s(id=%r, base_url=%r, manga_page=%r, chapiter_page=%r)" % (self.__class__.__name__, self.id, self.base_url, self.manga_page, self.chapiter_page)
