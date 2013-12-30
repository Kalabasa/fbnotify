from PluginBase import PluginBase
import pynotify

import time

class Plugin(PluginBase):
	''' Plugin for notifications using libnotify '''

	_handle = None
	_running = False

	def plugin_init(self):
		# Initialize pynotify
		pynotify.init('fbnotify')

		# Register to the 'notification' channel
		# to get messages about notifications
		self._handle = self._resource.register_listener(self, 'notification')
		self._running = True
		while self._resource and self._running:
			# Call PluginResource.receive to get messages from the channel
			self._resource.receive(self._handle)
			time.sleep(1)


	def plugin_destroy(self):
		# Stop the loop
		self._running = False
		pass

	def plugin_dependencies(self):
		# No dependencies
		return []

	def plugin_receive(self, channel, **msg):
		# Receiving a message from the 'notification' channel

		# Show notification
		n = pynotify.Notification(msg['title'], msg['body'], msg['xdg_icon'])
		if 'timeout' in msg:
			n.set_timeout(msg['timeout'])
		n.show()