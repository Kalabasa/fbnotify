from Feed import Feed
from Config import Config

import appdirs

import time
import os

class Notifier:
	''' main class '''

	def __init__(self):
		dirs = self.init_dirs()
		os.chdir(dirs.user_cache_dir)
		conf_file_path  = dirs.user_data_dir + '/fbnotify.conf'

		print('Working directory: ' + os.getcwd())
		print('Data directory: ' + dirs.user_data_dir)
		print('Cache directory: ' + dirs.user_cache_dir)
		print('Configuration file: ' + conf_file_path)
		print('')

		print('Initializing config...')
		self.conf = Config(conf_file_path)
		print('')

		print('Initializing feed...')
		self.feed = Feed(self.conf.feed.url)
		print('')

	def start(self):
		try:
			while True:
				print('Checking for new notifications...')
				new_items = self.feed.get_new_items()
				print('{0} new'.format(len(new_items)))
				if new_items:
					# NOTIFY
					print(new_items)
				self.adjust_interval(len(new_items))
				time.sleep(self.conf.feed.check_interval)
				print('')
		except KeyboardInterrupt:
			print('')
			print('Stopped')
			print('')
			pass


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
					print('Decreased check interval to {0}s'.format(ci))
			else:
				max_interval = 60 * 20
				if ci < max_interval:
					ci = ci * 9/5
					if ci > max_interval:
						ci = max_interval
					print('Increased check interval to {0}s'.format(ci))
			self.conf.feed.check_interval = ci


	def init_dirs(self):
		''' creates, if not existing, application directories '''

		dirs = appdirs.AppDirs('fbnotify', 'Kalabasa')
		conf_dir = dirs.user_data_dir
		cache_dir = dirs.user_cache_dir

		if not os.path.isdir(conf_dir):
			print('Created configuration directory ' + conf_dir)
			os.makedirs(conf_dir)

		if not os.path.isdir(cache_dir):
			print('Created cache directory ' + cache_dir)
			os.makedirs(cache_dir)

		return dirs