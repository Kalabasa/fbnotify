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

# plugin system implemented with some help from
# http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/

from PluginMessageSystem import PluginMessageSystem
from PluginContext import PluginContext

from threading import Thread
import ConfigParser
import collections
import re
import inspect
import imp
import os

import logging
logger = logging.getLogger(__name__)


PluginData = collections.namedtuple('PluginData', [
		'name',
		'module',
		'dependencies',
		'channels',
		'info'
	])


class PluginManager:

	dirs = []
	messaging = None
	_plugins = []
	_active = {}

	def __init__(self, dirs=None):
		if dirs:
			self.dirs.extend(dirs)
		self.messaging = PluginMessageSystem()


	def get_plugins(self):
		''' returns list of plugins that can be loaded '''

		if not self._plugins:
			self.refresh_plugins_list()
		return self._plugins


	def load(self, plugin_data, register_channels=True):
		''' loads a plugin '''

		logger.debug('Attempting to load plugin: ' + plugin_data.name + '...')

		if plugin_data.name in self._active:
			logger.warning(plugin_data.name + ' is already loaded!')
			return self._active[plugin_data.name]

		try:
			module = imp.load_module(plugin_data.module, *plugin_data.info)

			depend = plugin_data.dependencies
			if depend:
				for p in depend:
					logger.debug(plugin_data.name + ' depends on ' + p)
					if not self.load_by_name(p):
						logger.warning('Unable to satisfy the dependencies for ' + plugin_data.name)
						logger.warning('Unable to load plugin: ' + plugin_data.name)
						return None

			plugin = module.Plugin()

			if register_channels:
				for c in plugin_data.channels:
					self.messaging.register_plugin(plugin, c)

			plugin.__thread = Thread(target=lambda: self._start(plugin))
			plugin.__thread.daemon = True
			plugin.__thread.start()

			self._active[plugin_data.name] = plugin

			logger.info('Loaded plugin: ' + plugin_data.name)

		except Exception as e:
			logger.warning('Unable to load plugin: ' + plugin_data.name)
			logger.warning(str(e))
			return None

		return plugin

	def unload(self, name):
		''' unloads a plugin '''

		logger.debug('Attempting to unload plugin: ' + name + '...')

		if not name in self._active:
			logger.error('Plugin ' + name + ' nonexistent or inactive!')
			return

		plugin = self._active[name]
		del self._active[name]

		self.messaging.unregister_plugin(plugin)

		plugin.plugin_destroy()
		plugin.__thread.join()
		
		plugin.context = None

		logger.info('Unloaded plugin')


	def load_by_role(self, role):
		''' loads a plugin '''

		logger.debug('Finding plugin for role: ' + role)

		# Get plugins that satisfy this role
		candidate_plugins = []
		for p in self.get_plugins():
			if role in p.channels:
				candidate_plugins.append(p)

		if not candidate_plugins:
			logger.error('No plugin loaded for role: ' + role)
			return None

		# Sort by descending priority
		candidate_plugins.sort(key=lambda p: p.channels[role], reverse=True)

		# Try to load all starting from the highest
		for p in candidate_plugins:
			loaded = self.load(p, False)
			if loaded:
				for c in p.channels:
					self.messaging.register_plugin(loaded, c)
				return loaded

		return None


	def load_by_name(self, name):
		''' loads a plugin '''

		for p in self.get_plugins():
			if p.name == name:
				return self.load(p)

		logger.error('No plugin found with name: ' + name)

		return None

	def load_all(self):
		''' loads all plugins '''

		for p in self.get_plugins():
			self.load(p)

	def unload_all(self):
		''' unloads all plugins '''

		active = []
		for n in self._active:
			active.append(n)

		for n in reversed(active):
			self.unload(n)


	def refresh_plugins_list(self):
		''' refreshes the list of PluginData from plugins found '''

		del self._plugins[:]
		plugin_matcher = re.compile(r'^(.*\.plugin)$', re.IGNORECASE)

		for directory in self.dirs:
			if not os.path.isdir(directory):
				continue

			lst = os.listdir(directory)
			for name in lst:
				# Find subdirectories in the 'plugins' directory
				location = os.path.join(directory, name)
				if not os.path.isdir(location):
					continue

				# Find the '.plugin' file
				plugin_file_path = None
				for f in os.listdir(location):
					match = plugin_matcher.match(f)
					if match:
						plugin_file_path = os.path.join(location, match.group(1))
						break
				if not plugin_file_path:
					continue

				# Get plugin metadata
				cp = ConfigParser.ConfigParser()
				cp.read(plugin_file_path)

				module = cp.get('plugin', 'module').strip()
				dependencies = [x.strip() for x in cp.get('plugin', 'dependencies').strip().split(',') if x]
				channels = {}
				for c in cp.get('plugin', 'channels').strip().split(','):
					if not c:
						continue
					channel,priority = c.strip().split(':')
					channels[channel.strip()] = int(priority)

				try:
					info = imp.find_module(module, [location])
				except ImportError:
					continue

				plugin_data = PluginData(name, module, dependencies, channels, info)
				self._plugins.append(plugin_data)
	

	def _start(self, plugin):
		''' starts a plugin directly '''

		# Catch KeybInt to terminate the plugin on ^C
		try:
			plugin.plugin_init()
		except KeyboardInterrupt:
			pass
