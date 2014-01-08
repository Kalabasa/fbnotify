from PluginContext import PluginContext

from Queue import Queue
import collections

import logging
logger = logging.getLogger(__name__)


PluginQueue = collections.namedtuple('PluginQueue', ['plugin', 'queue'])
PluginMessage = collections.namedtuple('PluginMessage', ['channel', 'message'])

class PluginMessageSystem:
	'''
	handles the messages sent to and between plugins
	'''

	_listeners = {}

	def register_plugin(self, plugin, channel):
		''' subscribes a plugin to a channel '''

		plugin_queue = self.find_plugin_queue(plugin)
		if not plugin_queue:
			queue = Queue()
			plugin_queue = PluginQueue(plugin, queue)
			plugin.context = PluginContext(self, plugin, queue)

		if not channel in self._listeners:
			self._listeners[channel] = []
		self._listeners[channel].append(plugin_queue)

		return plugin.context

	def unregister_plugin(self, plugin):
		''' unregisters a plugin from all channels '''

		for c in self._listeners:
			l = self._listeners[c]
			l[:] = [q for q in l if q.plugin != plugin]

	def find_plugin_queue(self, plugin):
		''' return the PluginQueue associated with a plugin '''

		for c in self._listeners:
			for q in self._listeners[c]:
				if q.plugin == plugin:
					return q
		return None

	def send(self, channel, **kwargs):
		''' sends a message to all plugins subscribed to the channel '''

		pm = PluginMessage(channel, kwargs)
		if channel in self._listeners:
			for q in self._listeners[channel]:
				q.queue.put(pm)
