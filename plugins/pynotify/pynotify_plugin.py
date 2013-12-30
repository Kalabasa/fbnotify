from PluginBase import PluginBase
import pynotify

import time

class Plugin(PluginBase):
	''' Plugin for notifications using libnotify '''

	_handle = None
	_running = False

	def plugin_init(self):
		''' initialize anything here '''

		# Initialize pynotify
		pynotify.init('fbnotify')

		# Listen for notifications
		self._handle = self._resource.register_listener(self, 'notification')
		self._running = True
		while self._resource and self._running:
			self._resource.receive(self._handle)
			print(self._running)
			time.sleep(1)


	def plugin_destroy(self):
		''' cleanup everything here '''

		# Stop the loop
		self._running = False
		print('plugin_destroy')
		pass

	def plugin_dependencies(self):
		'''
		must return a list of plugin names that must be initialized
		before initializing this plugin
		'''

		# No dependencies
		return []

	def plugin_receive(self, **kwargs):
		''' called to receive a message from the plugin messaging system '''

		'''
		Receives
		'''
		pass