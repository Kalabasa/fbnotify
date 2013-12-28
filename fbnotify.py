#!/usr/bin/env python

import appdirs
import xnotify

import ConfigParser
import xml.etree.ElementTree as ElementTree
import email.utils
import urllib2
from datetime import datetime
import time
import os
import sys


# Application configuration
class Config:
	def __init__(self, file):
		file = os.path.abspath(file)

		# Default configutation
		self.feed_url = ''
		self.feed_interval = 60 * 4
		self.show_content = True
		self.itemize = 3
		self.notif_interval = 3

		# Read config file
		if not os.path.exists(file):
			print('FATAL: Config file {0} not found!'.format(file))
			self.save(file)
			print('Created new config file with default values')
			quit()
		cp = ConfigParser.RawConfigParser()
		try:
			cp.read(file)
		except ConfigParser.Error:
			print('FATAL: Unable to read config file {0}!'.format(file))
			quit()

		# Constraints
		feed_interval_min = 30
		notif_interval_min = 1
		itemize_min = 2

		# Section titles
		feed_section = 'Feed'
		notif_section = 'Notification'

		changed = False;

		try:
			self.feed_url = cp.get(feed_section, 'URL')
		except ConfigParser.Error:
			print('FATAL: In {0} [{1}], no URL found!'.format(file, feed_section))
			quit()

		try:
			self.feed_interval = cp.getint(feed_section, 'Interval')
		except ConfigParser.Error:
			print('In {0} [{1}], no Interval found!'.format(file, feed_section))
			print('Using default {0} seconds per check'.format(self.feed_interval))
		if self.feed_interval < feed_interval_min:
			print('WARNING: [{1}] Interval ({0}) too low'.format(self.feed_interval, feed_section))
			self.feed_interval = feed_interval_min
			changed = True;
			print('Setting Interval to minimum {0}'.format(self.feed_interval))

		try:
			self.show_content = cp.getboolean(notif_section, 'ShowContent')
		except ConfigParser.Error:
			print('In {0} [{1}], no ShowContent found'.format(file, notif_section))
			print('Using default {0}'.format(self.show_content))

		try:
			self.notif_interval = cp.getint(notif_section, 'Interval')
		except ConfigParser.Error:
			print('In {0} [{1}], no Interval found!'.format(file, notif_section))
			print('Using default {0} seconds per check'.format(self.notif_interval))
		if self.notif_interval < notif_interval_min:
			print('WARNING: [{1}] Interval ({0}) too low'.format(self.notif_interval, notif_section))
			self.notif_interval = notif_interval_min
			changed = True;
			print('Setting Interval to minimum {0}'.format(self.notif_interval))

		try:
			self.itemize = cp.getint(notif_section, 'Itemize')
		except ConfigParser.Error:
			print('In {0} [{0}], no Itemize found!'.format(file, notif_section))
			print('Using default {0}'.format(self.itemize))
		if self.itemize != 0 and self.itemize < itemize_min:
			print('WARNING: [{1}] Itemize ({0}) value invalid'.format(self.itemize, notif_section))
			self.itemize = itemize_min
			changed = True;
			print('Setting Itemize to {0}'.format(self.notif_interval))
		if self.itemize > 0 and not self.show_content:
			print('WARNING: Itemize but not ShowContent')
			print('No point in itemizing if content is not shown')
			self.show_content = True
			changed = True;
			print('Setting ShowContent to {0}'.format(self.show_content))


		# Save changes due to constraints
		if changed:
			self.save(file)

	# Save current configuration to file
	def save(self, file):
		cp = ConfigParser.RawConfigParser()
		cp.set(feed_section, 'URL', self.feed_url)
		cp.setint(feed_section, 'Interval', self.feed_interval)
		cp.setboolean(notif_section, 'ShowContent', self.show_content)
		cp.setint(notif_section, 'Itemize', self.itemize)
		cp.setint(notif_section, 'Interval', self.notif_interval)

		cfg_file = open(file,'w')
		cp.write(cfg_file)
		cfg_file.close()

# A notification
class Item:
	def __init__(self, text, link, dt):
		self.text = text
		self.link = link
		self.dt = dt;


# Global
config = None


# Main function
def main():
	global config

	print('Initializing..')

	dirs = appdirs.AppDirs('fbnotify', 'Kalabasa')
	conf_dir = dirs.user_data_dir
	cache_dir = dirs.user_cache_dir

	if not os.path.isdir(conf_dir):
		os.makedirs(conf_dir)
		print('Created configuration directory {0}'.format(conf_dir))

	if not os.path.isdir(cache_dir):
		os.makedirs(cache_dir)
		print('Created cache directory {0}'.format(cache_dir))

	config = Config(conf_dir + '/fbnotify.conf')
	os.chdir(cache_dir)

	xnotify.init('xnotify')

	print('')

	try:
		while poll(config.feed_url):
			print('..')
			time.sleep(config.feed_interval)
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
		last_mod = time.mktime_tz(email.utils.parsedate_tz(last_mod_str))
		time_f.close()
	except IOError:
		print('WARNING: Unable to open {0}'.format(last_mod_path))
		print('A new file will be created')

	# Read feed from URL
	try:
		request = urllib2.Request(feed_url)
		if last_mod != 0:
			request.add_header('If-Modified-Since', last_mod_str)
		opener = urllib2.build_opener()
		feed = opener.open(request)
	except urllib2.HTTPError as e:
		if e.code == 304: # Not modified
			print('No new notifications as of {0}'.format(time.strftime('%T')))
			return True
		print('FATAL: Unable to load feed URL')
		print('HTTP status {0}'.format(e.code))
		print('Reason {0}'.format(str(e.reason)))
		return False;
	except IOError:
		print('WARNING: Unable to load feed URL')
		return True

	# Save the modification time of the feed
	modified_str = feed.headers.get('Last-Modified')
	time_f = open(last_mod_path, 'w')
	time_f.write(modified_str)
	time_f.close

	# If first run / No last mod
	if last_mod == 0:
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
	print('{0} new notifications'.format(n))
	notify(news)

	return True


# Show notifications
def notify(notifs):
	title = 'Facebook'
	icon = 'facebook'
	urgency = 'NORMAL'

	n = len(notifs)
	if n > 1: # Many notifications

		# Sort by time
		notifs = sorted(notifs, key=lambda x: x.dt)

		# Say that there are many notifications
		xnotify.send(title, '{0} new notifications\n{1}'.format(n, format_time(notifs[0].dt)), icon, None, urgency, config.notif_interval)

		# Enumerate notifications if enabled
		if config.itemize >= n:
			for item in notifs:
				xnotify.send(title, format_item(item), icon, None, urgency, config.notif_interval)
				time.sleep(config.notif_interval)

	elif n == 1: # Single notification

		item = notifs[0]
		if config.show_content:
			xnotify.send(title, format_item(item), icon, None, urgency, None)
		else:
			xnotify.send(title, '1 new notification\n{0}'.format(format_time(item.dt)), icon, None, urgency, None)


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
