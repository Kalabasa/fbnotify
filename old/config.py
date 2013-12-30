#!/usr/bin/env python

import appdirs

import ConfigParser
import os


# Application configuration
class Config:
	def __init__(self, file):
		self.file = file = os.path.abspath(file)

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
			self.save()
			print('Created new config file with default values')
			os.chmod(file, 0600)

		cp = ConfigParser.RawConfigParser()
		try:
			cp.read(file)
		except ConfigParser.Error:
			print('FATAL: Unable to read config file {0}'.format(file))
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
			self.save()

	# Save current configuration to file
	def save(self):
		cp = ConfigParser.ConfigParser()

		cp.add_section(self._feed_section)
		cp.set(self._feed_section, 'url', self.feed_url)
		cp.set(self._feed_section, 'check_interval', self.check_interval)
		cp.set(self._feed_section, 'dynamic_interval', self.dynamic_interval)

		cp.add_section(self._notif_section)
		cp.set(self._notif_section, 'show_content', self.show_content)
		cp.set(self._notif_section, 'itemize', self.itemize)
		cp.set(self._notif_section, 'item_interval', self.item_interval)

		conf_f = open(self.file,'w')
		conf_f.write(
"""\
# Configuration File for fbnotify
# 
# KEEP THIS FILE PRIVATE
# 
# The feed URL contains sensitive information. It links to your notifications 
# feed in Facebook. Anyone with this URL can access your notifications and
# more, since it also contains your account's secret Facebook key.
# 
# Secure this file if you don't want your private feed accessed!
#
# On *nix, file permissions are automatically set so that only you and the 
# programs you run can read and write on this file. (Mode 0600)
#

""")
		cp.write(conf_f)
		conf_f.close()
		print('Saved configuration to {0}'.format(self.file))


# Creates application directories and files
def init():
	dirs = appdirs.AppDirs('fbnotify', 'Kalabasa')
	conf_dir = dirs.user_data_dir
	cache_dir = dirs.user_cache_dir

	if not os.path.isdir(conf_dir):
		os.makedirs(conf_dir)
		print('Created configuration directory {0}'.format(conf_dir))

	if not os.path.isdir(cache_dir):
		os.makedirs(cache_dir)
		print('Created cache directory {0}'.format(cache_dir))

	os.chdir(cache_dir)
	return Config(conf_dir + '/fbnotify.conf')

# Setup
def setup():
	cli_setup()
	return
	try:
		import wx
		wx_setup()
	except ImportError:
		cli_setup()

def cli_setup():
	print('fbnotify Setup')
	print('')

	conf = init()

	response = 'y'
	if True or not conf.feed_url:
		print('Feed URL setup')
		print('1. Go to fb.com/notifications to see Your Notifications.')
		print('2. Find the RSS feed in "Get notifications via: ..."')
		print('3. Copy the address of RSS feed.')
		print('4. Paste it here.')
		print('KEEP THIS URL SECRET since it contains your private feed')
		feed_url = raw_input('\tFeed URL [Blank to skip]: ')
		print('')
		print('Do you want to change advanced settings?')
		response = raw_input('\t[y/n]').lower()
		if response != 'y':
			print('Interpreting vague answer as "No"')
		print('')
	if response == 'y':
		print('fbnotify checks the notifications feed periodically.')
		print('Enter the interval in seconds between checks')
		check_interval = raw_input('\tInterval [Blank for default]: ')
		dynamic_interval = not bool(check_interval)
		print('')
		print('Show content in notifications?')
		show_content = raw_input('\tShow content [y/n]: ')
		# TODO


def wx_setup():
	import wx

	app = wx.App(False)
	frame = wx.Frame(None, wx.ID_ANY, 'fbnotify Configuration')
	frame.Show(True)
	app.MainLoop()

if __name__ == '__main__':
	setup()