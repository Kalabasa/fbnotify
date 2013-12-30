#!/usr/bin/env python

import config
from item import Item

import wx

import xml.etree.ElementTree as ElementTree
import email.utils
import urllib2
from datetime import datetime, timedelta
import time
import os


""" feed getter """
class Feeder:
	def __init__(self, conf):
		self.conf = conf

		# test URL
		request = urllib2.Request(self.conf.feed_url)
		opener = urllib2.build_opener()
		feed = opener.open(request)


	def poll(self):
		print('Checking for new notifications..')
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
			print('WARNING: Unable to open {0}'.format(last_mod_path))
			print('A new file will be created')

		# Read feed from URL
		is_modified = True
		try:
			request = urllib2.Request(self.conf.feed_url)
			if last_mod != 0:
				request.add_header('If-Modified-Since', last_mod_str)
			opener = urllib2.build_opener()
			feed = opener.open(request)
		except urllib2.HTTPError as e:
			# HTTP status not OK
			if e.code == 304: # Not modified
				is_modified = False
			else:
				print('WARNING: HTTPError' + str(e))
				print('Unable to load feed URL')
				print('HTTP status {0}'.format(e.code))
				print('Reason {0}'.format(str(e.reason)))
				return [];
		except IOError as e:
			# Connection error
			print('WARNING: IOError' + str(e))
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
				print 'Skipping all previous notifications..'
				#return True

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

			# Show notification about new items
			n = len(news)
			print('{0} new [{1}]'.format(n, time.strftime('%T')))
		else:
			# Not modified -> no new notifications
			print('None [{0}]'.format(time.strftime('%T')))

		# Adjust check interval if enabled
		if self.conf.dynamic_interval:
			if n == 0:
				max_interval = 60 * 20
				if self.conf.check_interval < max_interval:
					self.conf.check_interval = self.conf.check_interval * 9/5
					if self.conf.check_interval > max_interval:
						self.conf.check_interval = max_interval
					print('Increased check interval to {0}s'.format(self.conf.check_interval))
			else:
				min_interval = 15
				if self.conf.check_interval > min_interval:
					self.conf.check_interval = self.conf.check_interval * 1/5
					if self.conf.check_interval < min_interval:
						self.conf.check_interval = min_interval
					print('Decreased check interval to {0}s'.format(self.conf.check_interval))

		return news