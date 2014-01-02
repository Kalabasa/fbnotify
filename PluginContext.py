import Queue

class PluginContext:
	'''
	this is where plugin interacts
	'''

	_context = None
	_plugin = None
	_queue = None

	def __init__(self, context, plugin, queue):
		self._context = context
		self._plugin = plugin
		self._queue = queue

	def send(self, channel, **kwargs):
		''' sends a message to a channel '''

		self._context.send(channel, kwargs)

	def receive(self):
		''' processes the message queue to receive messages '''

		try:
			while True:
				message = self._queue.get(False)
				self._plugin.plugin_receive(message.channel, message.message)
		except Queue.Empty:
			pass
