# with some help from
# http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/

from PluginResource import PluginResource

from threading import Thread
import collections
import re
import imp
import os


PluginData = collections.namedtuple('PluginData', ['name', 'file_name', 'module'])

class PluginManager:
	''' manages plugins '''

	dirs = []
	resource = None
	_active = []

	def __init__(self, dirs=None):
		self.dirs.append(os.path.join(os.getcwd(), 'plugins'))
		if dirs:
			self.dirs.extend(dirs)

		self.resource = PluginResource()


	def find(self):
		''' returns a list of PluginData from plugins found '''

		plugins = []
		plugin_matcher = re.compile(r'^(.*_?plugin)\.pyc?$', re.IGNORECASE)

		for directory in self.dirs:
			lst = os.listdir(directory)
			for entry in lst:
				location = os.path.join(directory, entry)
				if not os.path.isdir(location):
					continue

				file_name = None
				for f in os.listdir(location):
					match = plugin_matcher.match(f)
					if match:
						file_name = match.group(1)
						break
				if not file_name:
					continue

				info = imp.find_module(file_name, [location])

				plugin_data = PluginData(name=entry, file_name=file_name, module=info)
				plugins.append(plugin_data)

		return plugins

	def load(self, plugin_data):
		''' loads a plugin '''

		module = imp.load_module(plugin_data.file_name, *plugin_data.module)
		plugin = module.Plugin()
		self._active.append(plugin)

		depend = plugin.plugin_dependencies()

		plugin._resource = self.resource
		plugin.__thread = Thread(target=plugin.plugin_init)
		plugin.__thread.start()

		print('Loaded ' + plugin_data.name + ' plugin')

		return plugin

	def load_by_name(self, name):
		''' loads a plugin '''
		for p in self.find():
			if p.name == name:
				self.load(p)

	def load_all(self):
		''' loads all plugins '''
		for p in self.find():
			self.load(p)

	def unload(self, plugin):
		''' unloads a plugin '''

		self._active.remove(plugin)

		plugin.plugin_destroy()
		plugin.__thread.join()
		plugin._resource = None

	def unload_all(self):
		''' unloads all plugins '''
		for p in self._active:
			self.unload(p)
