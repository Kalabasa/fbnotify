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
			logger.info('Initializing directories...')
			logger.debug('* Work: ' + os.getcwd())

			dirs = self.init_dirs()
			os.chdir(dirs.user_cache_dir)
			logger.debug('* Cache: ' + dirs.user_cache_dir)
			logger.info('* Data: ' + dirs.user_data_dir)

			plugin_dirs = []
			plugin_dirs.append(os.path.join(self.exec_dir, 'plugins'))
			plugin_dirs.append(os.path.join(dirs.user_data_dir, 'plugins'))
			for d in plugin_dirs:
				logger.info('* Plugins: ' + d)
			print('')

			logger.info('Initializing configuration...')
			conf_file_path = os.path.join(dirs.user_data_dir, 'fbnotify.conf')
			logger.info('* File: ' + conf_file_path)
			self.conf = Config(conf_file_path)
			print('')

			logger.info('Initializing feed...')
			self.feed = Feed(self.conf.feed.url)
			print('')

			logger.info('Initializing plugins...')
			self.plugin_man = PluginManager(plugin_dirs)
			self.plugin_man.load_by_role('notify')
			self.plugin_man.load_by_role('list')
			print('')

			logger.info('Initializing icons...')
			self.init_icons()
			print('')
		except Exception as e:
			logger.error(traceback.format_exc())
			self.bad_stop()


	def start(self):
		''' main loop '''

		try:
			while True:
				logger.info('Updating...')
				
				new_items = self.feed.get_new_items()
				self.notify_items(new_items)
				self.adjust_interval(len(new_items))

				time.sleep(self.conf.feed.check_interval)
				print('')
		except KeyboardInterrupt:
			print('')
			logger.info('Stopped')
			self.stop()
		except Exception as e:
			logger.error(traceback.format_exc())
			self.bad_stop()


	def bad_stop(self):
		''' bad things happened, so bad that the application must stop '''

		logger.error('Bad Exit!')
		self.stop()

	def stop(self):
		''' stop the application '''

		if self.plugin_man:
			logger.info('Unloading all plugins...')
			self.plugin_man.unload_all()
			
		logger.info('Exit')
		quit()


	def notify_items(self, items):
		''' shows notifications about items '''

		n = len(items)
		n_new_notifications = '{0} new notification{1}'.format(n, '' if n == 1 else 's')
		logger.info(n_new_notifications)
		if n == 0:
			return

		# Update item list
		self.plugin_man.messaging.send(
			'list',
			items = items
		)

		if n > 1: # Many notifications

			if self.conf.notification.itemize >= n:
				# Recite notifications if enabled
				interval = self.conf.notification.item_interval
				for item in sorted(items, key=lambda x: x.dt):
					self.notify(item.text, self.format_time(item.dt), interval)
					time.sleep(interval)
			else:
				# Declare multiple notifications instead of reciting
				dt = items[n-1].dt # Earliest notification date
				self.notify(n_new_notifications, self.format_time(dt))

		elif n == 1: # Single notification

			item = items[0]
			if self.conf.notification.show_content:
				self.notify(item.text, self.format_time(item.dt))
			else:
				self.notify(n_new_notifications, self.format_time(item.dt))

	def notify(self, title, body, timeout=10):
		''' shows a notification '''

		# This will send a message to any plugin
		# listening to the 'notify' channel
		self.plugin_man.messaging.send(
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
				min_interval = 5 # 5 seconds
				if ci > min_interval:
					ci = ci * 1/5
					if ci < min_interval:
						ci = min_interval
					logger.info('Decreased check interval to {0}s'.format(ci))
			else:
				max_interval = 60 * 20 # 20 minutes
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