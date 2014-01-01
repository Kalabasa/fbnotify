from PluginBase import PluginBase
import pynotify

import time

class Plugin(PluginBase):
	''' Plugin for notifications frontend using pynotify '''

	_running = False

	def plugin_init(self):
		# Initialize pynotify
		pynotify.init('fbnotify')

		# Register to the 'notify' channel
		# to get messages about notifications
		handle = self._resource.register_listener(self, 'notify')

		# Main loop
		self._running = True
		while self._resource and self._running:
			# Call PluginResource.receive to get messages from the channel
			self._resource.receive(handle)
			time.sleep(1)

	def plugin_destroy(self):
		# Stop the loop
		self._running = False
		pass

	def plugin_dependencies(self):
		# No dependencies
		return []

	def plugin_receive(self, channel, **msg):
		# Receiving a message from the 'notify' channel

		# Show notification
		n = pynotify.Notification(msg['title'], msg['body'], msg['xdg_icon'])
		if 'timeout' in msg:
			n.set_timeout(msg['timeout'])
		n.show()