# This file is part of fbnotify
#
# Copyright (c) 2014 Lean Rada <godffrey0@gmail.com>
# 
# fbnotify is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# fbnotify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with fbnotify.  If not, see <http://www.gnu.org/licenses/>.

from Feed import Feed
from Config import Config
from PluginManager import PluginManager
import icons

import appdirs

from datetime import datetime
import urllib2
import traceback
import time
import email.utils;
import os

import logging
logger = logging.getLogger(__name__)


class Notifier:
	''' main class '''

	program_dir = os.path.dirname(os.path.realpath(__file__))
	plugin_man = None
	plugin_context = None
	conf = None
	feed = None
	do_refresh = False

	def __init__(self):
		try:
			logger.info('Initializing directories...')

			dirs = self.init_dirs()
			os.chdir(dirs.user_cache_dir)
			logger.debug('* Cache: ' + dirs.user_cache_dir)
			logger.info('* Data: ' + dirs.user_data_dir)

			plugin_dirs = []
			plugin_dirs.append(os.path.join(self.program_dir, 'plugins'))
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
			logger.debug('* Blacklisted: ' + str(self.conf.program.plugin_blacklist))
			self.plugin_man = PluginManager(plugin_dirs, self.conf.program.plugin_blacklist)
			self.plugin_man.load_by_role('notify')
			self.plugin_man.load_by_role('list')
			self.plugin_man.load_by_role('status')
			self.plugin_context = self.plugin_man.messaging.register_plugin(self, 'fbnotify')
			print('')

			logger.debug('Work dir: ' + os.getcwd())
			print
		except Exception as e:
			logger.error(traceback.format_exc())
			self.bad_stop()


	def start(self):
		''' main loop '''

		try:
			while True:
				logger.info('Updating...' + ' [' + email.utils.formatdate(time.mktime(time.localtime()), True) + ']')
				
				# Update the feed
				self.plugin_man.messaging.send(
					'status',
					status='updating',
					description='Updating'
				)
				new_items = None
				try:
					new_items = self.feed.get_new_items()
				except IOError:
					# Error
					self.plugin_man.messaging.send(
						'status',
						status='error',
						description='Unable to load feed URL'
					)
					self.adjust_interval(0)

				# If new items are loaded
				if new_items is not None:
					self.plugin_man.messaging.send(
						'status',
						status='idle',
						description='Waiting'
					)
					self.notify_items(new_items)
					self.adjust_interval(len(new_items))

				# Wait
				count = 0
				while count < self.conf.feed.check_interval:
					time.sleep(0.25)
					count += 0.25
					self.plugin_context.receive()
					if self.do_refresh:
						break

				self.do_refresh = False

				print('')
		except KeyboardInterrupt:
			print('')
			logger.info('Stopped')
			self.stop()
		except Exception as e:
			logger.error(traceback.format_exc())
			self.bad_stop()
		self.bad_stop();


	def plugin_receive(self, channel, message):
		# Receiving a message from the 'fbnotify' channel
		if 'quit' in message:
			logger.debug('Quit requested')
			self.stop()
		elif 'refresh' in message:
			logger.debug('Refresh requested')
			self.do_refresh = True

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
				# Show individual notifications
				interval = self.conf.notification.item_interval
				for item in sorted(items, key=lambda x: x.dt):
					if item.image_path == None:
						self.notify(item.text, self.format_time(item.dt), timeout=interval, link=item.link)
					else:
						self.notify(item.text, self.format_time(item.dt), icon='file://' + item.image_path, timeout=interval, link=item.link)
					time.sleep(interval + 1)
			else:
				# Declare multiple notifications
				dt = items[n-1].dt # Earliest notification date
				self.notify(n_new_notifications, self.format_time(dt), link='www.facebook.com/notifications')

		else: # Single notification

			item = items[0]
			if self.conf.notification.show_content:
				if item.image_path == None:
					self.notify(item.text, self.format_time(item.dt), link=item.link)
				else:
					self.notify(item.text, self.format_time(item.dt), icon='file://' + item.image_path, link=item.link)
			else:
				self.notify(n_new_notifications, self.format_time(item.dt))

	def notify(self, title, body, icon=icons.xdg_icon, timeout=10, link=None):
		''' requests to show a notification '''

		logger.debug('Notify: ' + title + ' ' + body)

		# This will send a message to any plugin
		# listening to the 'notify' channel
		self.plugin_man.messaging.send(
			'notify',
			title = title,
			body = body,
			icon = icon,
			timeout = timeout,
			link = link
		)


	def adjust_interval(self, new):
		''' automatically adjust the feed check interval '''

		if self.conf.feed.dynamic_interval:
			ci = self.conf.feed.check_interval
			if new:
				min_interval = 15 # 15 seconds
				if ci > min_interval:
					ci = ci * 1/5
					if ci < min_interval:
						ci = min_interval
					logger.info('Decreased check interval to {0}s'.format(ci))
			else:
				max_interval = 60 * 20 # 20 minutes
				if ci < max_interval:
					ci = ci * 8/7
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


	def format_time(self, then):
		''' Formats relative time to the specified time '''


		now = datetime.now()
		if then >= now:
			text = 'Just now'
		else:
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
