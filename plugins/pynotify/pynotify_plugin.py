from PluginBase import PluginBase

import pynotify

import time

class Plugin(PluginBase):
	''' shows notifications using pynotify '''

	running = False

	def plugin_init(self):
		# Initialize pynotify
		pynotify.init('fbnotify')

		# Main loop
		self.running = True
		while self.context and self.running:
			# Call PluginContext.receive to get messages
			self.context.receive()
			time.sleep(1)

	def plugin_destroy(self):
		# Stop the main loop
		self.running = False
		pass

	def plugin_receive(self, channel, message):
		# Receiving a message from the 'notify' channel

		# Show notification
		n = pynotify.Notification(message['title'], message['body'], message['xdg_icon'])
		if 'timeout' in message:
			n.set_timeout(message['timeout'])
		n.show()