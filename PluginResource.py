from Queue import Queue
import collections

PluginChannel = collections.namedtuple('PluginChannel', ['plugin', 'queue'])

class PluginResource:
	'''
	plugin messaging system
	this is where plugin interacts
	'''

	_listeners = {}

	def __init__(self):
		pass

	def send(self, channel, **kwargs):
		''' sends a message to a channel '''

		if channel in self._listeners:
			for pc in self._listeners[channel]:
				pc.queue.put(kwargs)

	def receive(self, handle):
		'''requests for messages '''

		while not handle.queue.empty():
			kwargs = handle.queue.get()
			handle.plugin.receive_message(**kwargs)

	def register_listener(self, plugin, channel):
		'''
		register a plugin to receive messages from a channel
		returns a handle that is used to receive messages
		'''

		if not channel in self._listeners:
			self._listeners[channel] = []

		pc = PluginChannel(plugin=plugin, queue=Queue())
		self._listeners[channel].append(pc)
		return pc

	def unregister_listener(self, handle):
		''' unregister a plugin from a channel '''
		self._listeners[channel].remove(handle)