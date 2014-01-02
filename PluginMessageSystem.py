from PluginContext import PluginContext

from Queue import Queue
import collections


PluginQueue = collections.namedtuple('PluginQueue', ['plugin', 'queue'])
PluginMessage = collections.namedtuple('PluginMessage', ['channel', 'message'])

class PluginMessageSystem:
	'''
	handles the messages sent to and between plugins
	'''

	_listeners = {}

	def register_plugin(self, plugin, channels):
		''' subscribes a plugin to multiple channels '''
		queue = Queue()
		plugin_queue = PluginQueue(plugin, queue)
		context = PluginContext(self, plugin, queue)

		for c in channels:
			if not c in self._listeners:
				self._listeners[c] = []
			self._listeners[c].append(plugin_queue)

		return context

	def unregister_plugin(self, plugin):
		''' unregisters a plugin from all channels '''

		for c in self._listeners:
			l = self._listeners[c]
			l[:] = [q for q in l if q.plugin != plugin]

	def send(self, channel, message):
		''' sends a message to all plugins subscribed to the channel '''

		pm = PluginMessage(channel, message)
		if channel in self._listeners:
			for q in self._listeners[channel]:
				q.queue.put(pm)