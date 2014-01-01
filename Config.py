import ConfigParser
import os

import logging
logger = logging.getLogger(__name__)


class FeedConfig:
	def __init__(self):
		# Defaults
		self.url = ''
		self.check_interval = 60 * 4
		self.dynamic_interval = True

class NotificationConfig:
	def __init__(self):
		# Defaults
		self.show_content = True
		self.itemize = 3
		self.item_interval = 3


class Config:
	''' stores persistent application configurations '''

	def __init__(self, conf_file):
		self._file_path = os.path.abspath(conf_file)
		
		# Default configutation
		self.feed = FeedConfig()
		self.notification = NotificationConfig()

		# Section titles
		self._feed_section = 'feed'
		self._notif_section = 'notification'

		# Create config file
		if not os.path.exists(self._file_path):
			logger.info('Created new config file with default values')
			self.save()
			os.chmod(self.file_path, 0600)

		# Read config file
		cp = ConfigParser.ConfigParser()
		cp.read(self._file_path)

		# Constraints
		check_interval_min = 30
		item_interval_min = 1
		itemize_min = 2

		changed = False;

		try:
			self.feed.url = cp.get(self._feed_section, 'url')
		except ConfigParser.Error as e:
			logger.error('FATAL: In {0} [{1}], no url found!'.format(self._file_path, self._feed_section))
			raise e

		try:
			self.feed.check_interval = cp.getint(self._feed_section, 'check_interval')
		except ConfigParser.Error:
			logger.info('In {0} [{1}], no check_interval found!'.format(self._file_path, self._feed_section))
			logger.info('Using default {0} seconds per check'.format(self.feed.check_interval))
			changed = True;
		if self.feed.check_interval < check_interval_min:
			logger.info('[{1}] check_interval ({0}) too low'.format(self.feed.check_interval, self._feed_section))
			self.feed.check_interval = check_interval_min
			logger.info('Setting interval to minimum {0}'.format(self.feed.check_interval))
			changed = True;

		try:
			self.feed.dynamic_interval = cp.getboolean(self._feed_section, 'dynamic_interval')
		except ConfigParser.Error:
			logger.info('In {0} [{1}], no dynamic_interval found!'.format(self._file_path, self._feed_section))
			logger.info('Using default {0}'.format(self.feed.dynamic_interval))
			changed = True;

		try:
			self.notification.show_content = cp.getboolean(self._notif_section, 'show_content')
		except ConfigParser.Error:
			logger.info('In {0} [{1}], no show_content found!'.format(self._file_path, self._notif_section))
			logger.info('Using default {0}'.format(self.notification.show_content))
			changed = True;

		try:
			self.notification.item_interval = cp.getint(self._notif_section, 'item_interval')
		except ConfigParser.Error:
			logger.info('In {0} [{1}], no item_interval found!'.format(self._file_path, self._notif_section))
			logger.info('Using default {0} seconds per item'.format(self.notification.item_interval))
			changed = True;
		if self.notification.item_interval < item_interval_min:
			logger.info('[{1}] item_interval ({0}) too low'.format(self.notification.item_interval, self._notif_section))
			self.notification.item_interval = item_interval_min
			logger.info('Setting item_interval to minimum {0}'.format(self.notification.item_interval))
			changed = True;

		try:
			self.notification.itemize = cp.getint(self._notif_section, 'itemize')
		except ConfigParser.Error:
			logger.info('In {0} [{1}], no itemize found!'.format(self._file_path, self._notif_section))
			logger.info('Using default {0}'.format(self.notification.itemize))
			changed = True;
		if self.notification.itemize != 0 and self.notification.itemize < itemize_min:
			logger.info('[{1}] itemize ({0}) value invalid'.format(self.notification.itemize, self._notif_section))
			self.notification.itemize = itemize_min
			changed = True;
			logger.info('Setting itemize to {0}'.format(self.notification.item_interval))
		if self.notification.itemize > 0 and not self.notification.show_content:
			logger.info('itemize=True but show_content=False')
			logger.info('No point in itemizing if content is not shown')
			self.notification.show_content = True
			logger.info('Setting show_content to {0}'.format(self.notification.show_content))
			changed = True;

		# Save changes due to constraints
		if changed:
			self.save()

	def save(self):
		''' saves current configuration to file '''

		cp = ConfigParser.ConfigParser()

		cp.add_section(self._feed_section)
		cp.set(self._feed_section, 'url', self.feed.url)
		cp.set(self._feed_section, 'check_interval', self.feed.check_interval)
		cp.set(self._feed_section, 'dynamic_interval', self.feed.dynamic_interval)

		cp.add_section(self._notif_section)
		cp.set(self._notif_section, 'show_content', self.notification.show_content)
		cp.set(self._notif_section, 'itemize', self.notification.itemize)
		cp.set(self._notif_section, 'item_interval', self.notification.item_interval)

		conf_file = open(self.file_path,'w')
		conf_file.write(
"""\
# Configuration file for fbnotify
# 
# KEEP THIS FILE PRIVATE
# 
# Anyone with this URL can access your notifications and more, since it also 
# contains your account's secret Facebook key.
# 
# Secure this file if you don't want your private feed accessed!
#
# On *nix, file permissions are automatically set (Mode 0600).
#

""")
		self.cp.write(conf_file)
