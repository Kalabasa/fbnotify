from Item import Item

from datetime import datetime, timedelta
import xml.etree.ElementTree as ElementTree
import email.utils
import urllib2
import time
import os

import logging
logger = logging.getLogger(__name__)


class Feed:
	''' the notifications feed '''

	feed_url = None
	link = None
	_last_mod_path = None

	def __init__(self, feed_url):
		self.feed_url = feed_url
		self.link = ''
		self._last_mod_path = os.path.abspath('.last-modified')


	def get_new_items(self):
		''' returns new items from the feed '''

		# Get the modification time of the feed for the last time I checked
		last_mod_str = None
		last_mod = 0
		try:
			last_mod_str = open(self._last_mod_path, 'r').readline()
			last_mod = email.utils.mktime_tz(email.utils.parsedate_tz(last_mod_str))
		except IOError:
			logger.warning('Unable to read ' + self._last_mod_path)
			logger.info('A new file is created')
			last_mod = 0#time.mktime(time.localtime())
			last_mod_str = email.utils.formatdate(last_mod)
			open(self._last_mod_path, 'w').write(last_mod_str)
			

		# Read feed from URL
		is_modified = True
		try:
			request = urllib2.Request(self.feed_url)
			request.add_header('If-Modified-Since', last_mod_str)
			opener = urllib2.build_opener()
			feed = opener.open(request)
		except urllib2.HTTPError as e:
			if e.code == 304: # Not modified
				is_modified = False
			else: # Bad HTTP status
				raise e
		except IOError as e:
			# Connection error
			logger.error('Unable to load feed URL')
			return []

		n = 0
		news = []
		if is_modified:
			# Save the modification time of the feed
			modified_str = feed.headers.get('Last-Modified')
			open(self._last_mod_path, 'w').write(modified_str)

			# Read and parse the feed
			xml = feed.read()
			tree = ElementTree.fromstring(xml)

			# Get link
			self.link = tree[0].find('link').text

			# Get new items
			for node in tree.iter('item'):
				pub = email.utils.mktime_tz(email.utils.parsedate_tz(node.find('pubDate').text))
				if pub <= last_mod:
					break
				title = node.find('title').text
				link = node.find('link').text
				dt = datetime.fromtimestamp(pub)
				news.append(Item(title, link, dt))

		return news