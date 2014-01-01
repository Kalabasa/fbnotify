from Feed import Feed
from Config import Config
from PluginManager import PluginManager

import appdirs

from datetime import datetime,timedelta
import urllib2
import traceback
import time
import os

import logging
logger = logging.getLogger(__name__)


class Notifier:
	''' main class '''

	exec_dir = os.getcwd()
	plugin_man = None
	conf = None
	feed = None

	def __init__(self):
		try:
			print 123
			logger.info('Initializing directories...')
			logger.info('Working directory: ' + os.getcwd())

			dirs = self.init_dirs()
			os.chdir(dirs.user_cache_dir)
			logger.info('Data directory: ' + dirs.user_data_dir)
			logger.info('Cache directory: ' + dirs.user_cache_dir)

			plugin_dirs = []
			plugin_dirs.append(os.path.join(self.exec_dir, 'plugins'))
			plugin_dirs.append(os.path.join(dirs.user_data_dir, 'plugins'))
			for d in plugin_dirs:
				logger.info('Plugin directory:' + d)

			logger.info('Initializing configuration...')
			conf_file_path = os.path.join(dirs.user_data_dir, 'fbnotify.conf')
			logger.info('Configuration file: ' + conf_file_path)
			self.conf = Config(conf_file_path)

			logger.info('Initializing feed...')
			self.feed = Feed(self.conf.feed.url)

			logger.info('Initializing plugins...')
			self.plugin_man = PluginManager(plugin_dirs)
			self.plugin_man.load_all()

			logger.info('Initializing icons...')
			self.init_icons()
		except Exception as e:
			logger.error(traceback.format_exc())
			logger.info('Bad exit')
			quit()


	def start(self):
		try:
			while True:
				logger.info('Checking for new notifications...')

				new_items = self.feed.get_new_items()
				self.notify_items(new_items)
				self.adjust_interval(len(new_items))

				time.sleep(self.conf.feed.check_interval)
				logger.info('')
		except KeyboardInterrupt:
			self.plugin_man.unload_all()
			logger.info('Stopped')
		except Exception as e:
			logger.error(traceback.format_exc())
			logger.info('Bad exit')
			quit()


	def notify_items(self, items):
		''' shows notifications about items '''

		n = len(items)
		n_new_notifications = '{0} new notification{1}'.format(n, '' if n == 1 else 's')
		logger.info(n_new_notifications)
		if n == 0:
			return

		# Update item list
		self.plugin_man.context.send(
			'list',
			items = items
		)

		if n > 1: # Many notifications

			# Declare multiple notifications
			dt = items[n-1].dt # Earliest
			self.notify(n_new_notifications, self.format_time(dt))

			# Enumerate notifications if enabled
			interval = self.conf.notification.item_interval
			if self.conf.notification.itemize >= n:
				for item in sorted(items, key=lambda x: x.dt):
					self.notify(item.text, self.format_time(item.dt), interval)
					time.sleep(interval)

		elif n == 1: # Single notification

			item = items[0]
			if conf.show_content:
				self.notify(item.text, self.format_time(item.dt))
			else:
				self.notify(n_new_notifications, self.format_time(item.dt))

	def notify(self, title, body, timeout=10):
		''' shows a notification '''

		# This will send a message to any plugin
		# listening to the 'notify' channel
		self.plugin_man.context.send(
			'notify',
			title = title,
			body = body,
			timeout = timeout,
			xdg_icon = self.xdg_icon,
			icon_path = self.icon_path,
			icon_data = self.icon_data,
		)


	def adjust_interval(self, new):
		''' automatically adjust the feed check interval '''

		if self.conf.feed.dynamic_interval:
			ci = self.conf.feed.check_interval
			if new:
				min_interval = 15
				if ci > min_interval:
					ci = ci * 1/5
					if ci < min_interval:
						ci = min_interval
					logger.info('Decreased check interval to {0}s'.format(ci))
			else:
				max_interval = 60 * 20
				if ci < max_interval:
					ci = ci * 9/5
					if ci > max_interval:
						ci = max_interval
					logger.info('Increased check interval to {0}s'.format(ci))
			self.conf.feed.check_interval = ci


	def init_dirs(self):
		''' creates, if not existing, application directories '''

		dirs = appdirs.AppDirs('fbnotify', 'Kalabasa')
		conf_dir = dirs.user_data_dir
		cache_dir = dirs.user_cache_dir

		if not os.path.isdir(conf_dir):
			logger.info('Created configuration directory ' + conf_dir)
			os.makedirs(conf_dir)

		if not os.path.isdir(cache_dir):
			logger.info('Created cache directory ' + cache_dir)
			os.makedirs(cache_dir)

		return dirs

	def init_icons(self):
		# Set icon
		self.xdg_icon = 'facebook'
		self.icon_path = None
		self.icon_data = open(self.icon_path, 'rb').read() if self.icon_path else None


	def format_time(self, then):
		''' Formats relative time to the specified time '''

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