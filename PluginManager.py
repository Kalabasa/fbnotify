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
		'roles',
		'info'
	])


class PluginManager:

	dirs = []
	messaging = None
	_plugins = []
	_active = []

	def __init__(self, dirs=None):
		if dirs:
			self.dirs.extend(dirs)
		self.messaging = PluginMessageSystem()


	def get_plugins(self):
		''' returns list of plugins that can be loaded '''

		if not self._plugins:
			self.refresh_plugins_list()
		return self._plugins


	def load(self, plugin_data):
		''' loads a plugin '''

		try:
			module = imp.load_module(plugin_data.module, *plugin_data.info)

			depend = plugin_data.dependencies
			if depend:
				logger.info('Loading dependencies for plugin: ' + plugin_data.name)
				for p in depend:
					logger.info('Depends on ' + p)
					if not self.load_by_name(p):
						logger.warning('Unable to satisfy the dependencies for ' + plugin_data.name)
						logger.warning('Unable to load plugin: ' + plugin_data.name)
						return None

			plugin = module.Plugin()

			if plugin_data.channels:
				plugin.context = self.messaging.register_plugin(plugin, plugin_data.channels)

			plugin.__thread = Thread(target=lambda: self._start(plugin))
			plugin.__thread.daemon = True
			plugin.__thread.start()

			self._active.append(plugin)

			logger.info('Loaded plugin: ' + plugin_data.name)

		except ImportError as e:
			logger.warning('Unable to load plugin: ' + plugin_data.name)
			logger.warning(str(e))
			return None

		return plugin

	def unload(self, plugin):
		''' unloads a plugin '''

		logger.info('Unloading plugin module: ' + os.path.basename(inspect.getfile(plugin.__class__)))

		self._active.remove(plugin)

		self.messaging.unregister_plugin(plugin)

		plugin.plugin_destroy()
		plugin.__thread.join()
		
		plugin.context = None

		logger.info('Unloaded plugin')


	def load_by_role(self, role):
		''' loads a plugin '''

		candidate_plugins = []
		for p in self.get_plugins():
			if role in p.roles:
				candidate_plugins.append(p)

		if not candidate_plugins:
			return None

		highest = candidate_plugins[0]
		for p in candidate_plugins:
			if p.roles[role] > highest.roles[role]:
				highest = p

		return self.load(highest)


	def load_by_name(self, name):
		''' loads a plugin '''

		for p in self.get_plugins():
			if p.name == name:
				return self.load(p)
		return None

	def load_all(self):
		''' loads all plugins '''

		for p in self.get_plugins():
			self.load(p)

	def unload_all(self):
		''' unloads all plugins '''

		for p in self._active:
			self.unload(p)


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
				channels = [x.strip() for x in cp.get('plugin', 'channels').strip().split(',') if x]
				roles = {}
				for r in cp.get('plugin', 'roles').strip().split(','):
					if not r:
						continue
					role,priority = r.strip().split(':')
					roles[role.strip()] = int(priority)

				try:
					info = imp.find_module(module, [location])
				except ImportError:
					continue

				plugin_data = PluginData(name, module, dependencies, channels, roles, info)
				self._plugins.append(plugin_data)
	

	def _start(self, plugin):
		''' starts a plugin directly '''

		# Catch KeybInt to terminate the plugin on ^C
		try:
			plugin.plugin_init()
		except KeyboardInterrupt:
			pass
