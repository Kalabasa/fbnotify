from Item import Item

import urllib2
import httplib

class HeadRequest(urllib2.Request):
	''' Request headers of URL instead of content '''
	def get_method(self):
		return "HEAD"

class Feed:
	''' The notifications feed '''

	def __init__(self, feed_url):
		self.feed_url = feed_url
		self.test_feed_url()

	def test_feed_url(self):
		code = urllib2.urlopen(HeadRequest(self.feed_url)).info
		if code != 200:
			return False
		

	def get_new_items(self):
		last_mod_path = os.path.abspath('.last-modified')

		# Get the modification time of the feed for the last time I checked
		last_mod_str = None
		last_mod = 0
		try:
			time_f = open(last_mod_path, 'r')
			last_mod_str = time_f.readline()
			last_mod = email.utils.mktime_tz(email.utils.parsedate_tz(last_mod_str))
			time_f.close()
		except IOError:
			print('ERROR: Unable to open {0}'.format(last_mod_path))

		# Read feed from URL
		is_modified = True
		try:
			request = urllib2.Request(self.feed_url)
			if last_mod != 0:
				request.add_header('If-Modified-Since', last_mod_str)
			opener = urllib2.build_opener()
			feed = opener.open(request)
		except urllib2.HTTPError as e:
			# HTTP status not OK
			if e.code == 304: # Not modified
				is_modified = False
			else:
				print('ERROR: HTTPError ' + str(e))
				print('Unable to load feed URL')
				print('Code: {0}'.format(e.code))
				print('Reason: {0}'.format(str(e.reason)))
				return [];
		except IOError as e:
			# Connection error
			print('ERROR: IOError ' + str(e))
			print('Unable to load feed URL')
			return []

		n = 0
		news = []
		if is_modified:
			# Save the modification time of the feed
			modified_str = feed.headers.get('Last-Modified')
			time_f = open(last_mod_path, 'w')
			time_f.write(modified_str)
			time_f.close

			# If first run or no last mod
			if last_mod == 0:
				return []

			# Read and parse the feed
			xml = feed.read()
			tree = ElementTree.fromstring(xml)

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