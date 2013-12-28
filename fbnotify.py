#!/usr/bin/env python

import ConfigParser
import time
import urllib2
import xml.etree.ElementTree as ElementTree
import email.utils
import pynotify
import os


# Application configuration
class Config:
	def __init__(self, file):
		# Default configutation
		self.feed_url = ''
		self.feed_interval = 60 * 4
		self.show_content = True
		self.itemize = 0
		self.notif_interval = 2

		# Read config file
		if not os.path.exists(file):
			print('FATAL: Config file {0} not found in {1}!'.format(file, os.getcwd()))
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
	def __init__(self, text, link, time):
		self.text = text
		self.link = link
		self.time = time;


# Global
config = None


# Main function
def main():
	global config

	print('Initializing..')

	work_dir = os.path.expanduser('~') + '/.fbnotify/'
	if not os.path.isdir(work_dir):
		os.makedirs(work_dir)
		print('Created configuration directory {0}'.format(work_dir)
	os.chdir(work_dir)
	config = Config('fbnotify.cfg')
	pynotify.init('fbnotify')

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
	last_mod_path = '.last-modified'

	# Get the modification time of the feed for the last time I checked
	last_mod_str = None
	last_mod = 0
	try:
		time_f = open(last_mod_path, 'r')
		last_mod_str = time_f.readline()
		last_mod = time.mktime(email.utils.parsedate(last_mod_str))
		time_f.close()
	except IOError:
		print('WARNING: Unable to open {0}'.format(last_mod_path))

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
	modified_str = feed.headers.get("Last-Modified")
	time_f = open(last_mod_path, 'w')
	time_f.write(modified_str)
	time_f.close

	# Read and parse the feed
	xml = feed.read()
	tree = ElementTree.fromstring(xml)

	# Get new items
	news = []
	for node in tree.iter('item'):
		pub = email.utils.mktime_tz(email.utils.parsedate_tz(node.find('pubDate').text))
		if pub <= last_mod:
			break
		news.append(Item(node.find('title').text, node.find('link').text, pub))

	# Show notification about new items
	n = len(news)
	print('{0} new notifications'.format(n))
	notify(news)

	return True


# Show notifications
def notify(notifs):
	title = "Facebook"
	icon = "facebook"

	n = len(notifs)
	if n > 0:
		if n > 1: # Many notifications

			# Say that there are many notifications
			notif = pynotify.Notification(title, "{0} new notifications".format(n), icon)
			notif.show()

			# Enumerate notifications if enabled
			if config.itemize >= n:
				for item in sorted(notifs, key=lambda x: x.time):
					notif = pynotify.Notification(title, format_item(item), icon)
					notif.show()
					notif.set_timeout(config.notif_interval)
					time.sleep(config.notif_interval)

		else: # Single notification

			if config.show_content:
				notif = pynotify.Notification(title, format_item(notifs[0]), icon)
			else:
				notif = pynotify.Notification(title, "1 new notification", icon)

			notif.show()


# Format notification
def format_item(item):
	text = item.text
	text += '\n'
	text += format_time(item.time)
	return text


# Format time as relative time
def format_time(time):
	current = time.localtime()
	return "{0} seconds ago".format(time - current)


if __name__ == "__main__":
	main()
