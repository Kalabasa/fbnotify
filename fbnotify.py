#!/usr/bin/env python

import config

import xnotify

import xml.etree.ElementTree as ElementTree
import email.utils
import urllib2
from datetime import datetime
import time
import os


# A notification
class Item:
	def __init__(self, text, link, dt):
		self.text = text
		self.link = link
		self.dt = dt


# Global
conf = None


# Main function
def main():
	global conf

	print('Initializing..')

	conf = config.init()
	print('Working directory: {0}'.format(os.getcwd()))

	xnotify.init('kalabasa.fbnotify')

	print('')

	try:
		while poll(conf.feed_url):
			time.sleep(conf.check_interval)
			print('')
	except KeyboardInterrupt:
		print('')
		print('Stopped')
		print('')


# Checks and notifies new notifications
def poll(feed_url):
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
		request = urllib2.Request(feed_url)
		if last_mod != 0:
			request.add_header('If-Modified-Since', last_mod_str)
		opener = urllib2.build_opener()
		feed = opener.open(request)
	except ValueError:
		# Invaid URL value
		print('FATAL: Invalid feed url')
		return False
	except urllib2.HTTPError as e:
		# HTTP status not OK
		if e.code == 304: # Not modified
			is_modified = False
		else:
			print('FATAL: HTTPError' + str(e))
			print('Unable to load feed URL')
			print('HTTP status {0}'.format(e.code))
			print('Reason {0}'.format(str(e.reason)))
			return False;
	except IOError as e:
		# Connection error
		print('WARNING: IOError' + e)
		print('Unable to load feed URL')
		return True

	n = 0
	if is_modified:
		# Save the modification time of the feed
		modified_str = feed.headers.get('Last-Modified')
		time_f = open(last_mod_path, 'w')
		time_f.write(modified_str)
		time_f.close

		# If first run or no last mod
		if last_mod == 0:
			print 'Skipping all previous notifications..'
			return True

		# Read and parse the feed
		xml = feed.read()
		tree = ElementTree.fromstring(xml)

		# Get new items
		news = []
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
		notify(news)
	else:
		# Not modified -> no new notifications
		print('None [{0}]'.format(time.strftime('%T')))

	# Adjust check interval if enabled
	if conf.dynamic_interval:
		if n == 0:
			max_interval = 60 * 20
			if conf.check_interval < max_interval:
				conf.check_interval = conf.check_interval * 3/2
				if conf.check_interval > max_interval:
					conf.check_interval = max_interval
				print('Increased check interval to {0}s'.format(conf.check_interval))
		else:
			min_interval = 15
			if conf.check_interval > min_interval:
				conf.check_interval = conf.check_interval * 1/6
				if conf.check_interval < min_interval:
					conf.check_interval = min_interval
				print('Decreased check interval to {0}s'.format(conf.check_interval))

	return True


# Show notifications
def notify(notifs):
	title = 'fbnotify'
	icon = 'facebook'
	wx_icon = None # TODO ???
	urgency = 'NORMAL'

	n = len(notifs)
	if n > 1: # Many notifications

		# Sort by time
		notifs = sorted(notifs, key=lambda x: x.dt)

		# Say that there are many notifications
		xnotify.send(title, '{0} new notifications\n{1}'.format(n, format_time(notifs[0].dt)), icon, wx_icon, urgency, conf.item_interval)

		# Enumerate notifications if enabled
		if conf.itemize >= n:
			for item in notifs:
				xnotify.send(title, format_item(item), icon, wx_icon, urgency, conf.item_interval)
				time.sleep(conf.item_interval)

	elif n == 1: # Single notification

		item = notifs[0]
		if conf.show_content:
			xnotify.send(title, format_item(item), icon, wx_icon, urgency, None)
		else:
			xnotify.send(title, '1 new notification\n{0}'.format(format_time(item.dt)), icon, wx_icon, urgency, None)


# Format notification
def format_item(item):
	text = item.text
	text += '\n'
	text += format_time(item.dt)
	return text


# Format time as relative time
def format_time(then):
	now = datetime.now()
	delta = now - then
	if delta.days >= 1:
		text = '{0} day{1} ago'.format(delta.days, '' if delta.days == 1 else 's')
	elif delta.seconds >= 3600:
		hours = delta.seconds / 3600
		text = '{0} hour{1} ago'.format(hours, '' if hours == 1 else 's')
	elif delta.seconds >= 60:
		minutes = delta.seconds / 60
		text = '{0} minute{1} ago'.format(minutes, '' if minutes == 1 else 's')
	elif delta.seconds >= 30:
		text = '{0} second{1} ago'.format(delta.seconds, '' if delta.seconds == 1 else 's')
	else:
		text = 'Just now'
	return text


if __name__ == '__main__':
	main()
