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
		self.check_interval = 60 * 4
		self.dynamic_interval = True
		self.show_content = True
		self.itemize = 3
		self.item_interval = 3

		# Section titles
		self._feed_section = 'Feed'
		self._notif_section = 'Notification'

		# Read config file
		if not os.path.exists(file):
			print('WARNING: Config file {0} not found!'.format(file))
			self.save(file)
			print('Created new config file with default values')

		cp = ConfigParser.RawConfigParser()
		try:
			cp.read(file)
		except ConfigParser.Error:
			print('FATAL: Unable to read config file {0}!'.format(file))
			quit()

		# Constraints
		check_interval_min = 30
		item_interval_min = 1
		itemize_min = 2

		changed = False;

		try:
			self.feed_url = cp.get(self._feed_section, 'url')
		except ConfigParser.Error:
			print('FATAL: In {0} [{1}], no url found!'.format(file, self._feed_section))
			quit()

		try:
			self.check_interval = cp.getint(self._feed_section, 'check_interval')
		except ConfigParser.Error:
			print('In {0} [{1}], no check_interval found!'.format(file, self._feed_section))
			print('Using default {0} seconds per check'.format(self.check_interval))
			changed = True;
		if self.check_interval < check_interval_min:
			print('WARNING: [{1}] check_interval ({0}) too low'.format(self.check_interval, self._feed_section))
			self.check_interval = check_interval_min
			print('Setting interval to minimum {0}'.format(self.check_interval))
			changed = True;

		try:
			self.dynamic_interval = cp.getboolean(self._feed_section, 'dynamic_interval')
		except ConfigParser.Error:
			print('In {0} [{1}], no dynamic_interval found!'.format(file, self._feed_section))
			print('Using default {0}'.format(self.dynamic_interval))
			changed = True;

		try:
			self.show_content = cp.getboolean(self._notif_section, 'show_content')
		except ConfigParser.Error:
			print('In {0} [{1}], no show_content found!'.format(file, self._notif_section))
			print('Using default {0}'.format(self.show_content))
			changed = True;

		try:
			self.item_interval = cp.getint(self._notif_section, 'item_interval')
		except ConfigParser.Error:
			print('In {0} [{1}], no item_interval found!'.format(file, self._notif_section))
			print('Using default {0} seconds per item'.format(self.item_interval))
			changed = True;
		if self.item_interval < item_interval_min:
			print('WARNING: [{1}] item_interval ({0}) too low'.format(self.item_interval, self._notif_section))
			self.item_interval = item_interval_min
			print('Setting item_interval to minimum {0}'.format(self.item_interval))
			changed = True;

		try:
			self.itemize = cp.getint(self._notif_section, 'itemize')
		except ConfigParser.Error:
			print('In {0} [{1}], no itemize found!'.format(file, self._notif_section))
			print('Using default {0}'.format(self.itemize))
			changed = True;
		if self.itemize != 0 and self.itemize < itemize_min:
			print('WARNING: [{1}] itemize ({0}) value invalid'.format(self.itemize, self._notif_section))
			self.itemize = itemize_min
			changed = True;
			print('Setting itemize to {0}'.format(self.item_interval))
		if self.itemize > 0 and not self.show_content:
			print('WARNING: itemize but not ShowContent')
			print('No point in itemizing if content is not shown')
			self.show_content = True
			print('Setting show_content to {0}'.format(self.show_content))
			changed = True;

		# Save changes due to constraints
		if changed:
			self.save(file)

	# Save current configuration to file
	def save(self, file):
		cp = ConfigParser.ConfigParser()

		cp.add_section(self._feed_section)
		cp.set(self._feed_section, 'url', self.feed_url)
		cp.set(self._feed_section, 'check_interval', self.check_interval)
		cp.set(self._feed_section, 'dynamic_interval', self.dynamic_interval)

		cp.add_section(self._notif_section)
		cp.set(self._notif_section, 'show_content', self.show_content)
		cp.set(self._notif_section, 'itemize', self.itemize)
		cp.set(self._notif_section, 'item_interval', self.item_interval)

		cfg_file = open(file,'w')
		cp.write(cfg_file)
		cfg_file.close()
		print('Saved configuration to {0}'.format(file))

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
			time.sleep(config.check_interval)
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
	if config.dynamic_interval:
		if n == 0:
			max_interval = 60 * 20
			if config.check_interval < max_interval:
				config.check_interval = config.check_interval * 3/2
				if config.check_interval > max_interval:
					config.check_interval = max_interval
				print('Increased check_interval to {0}'.format(config.check_interval))
		else:
			min_interval = 15
			if config.check_interval > min_interval:
				config.check_interval = config.check_interval * 1/6
				if config.check_interval < min_interval:
					config.check_interval = min_interval
				print('Decreased check_interval to {0}'.format(config.check_interval))

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
		xnotify.send(title, '{0} new notifications\n{1}'.format(n, format_time(notifs[0].dt)), icon, wx_icon, urgency, config.item_interval)

		# Enumerate notifications if enabled
		if config.itemize >= n:
			for item in notifs:
				xnotify.send(title, format_item(item), icon, wx_icon, urgency, config.item_interval)
				time.sleep(config.item_interval)

	elif n == 1: # Single notification

		item = notifs[0]
		if config.show_content:
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
