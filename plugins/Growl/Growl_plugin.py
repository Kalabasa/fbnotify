from PluginBase import PluginBase

import gntp.notifier

import time

class Plugin(PluginBase):
	''' shows notifications using Growl '''

	growl = None
	running = False

	def plugin_init(self):
		# Register to Growl
		self.growl = gntp.notifier.GrowlNotifier(
			applicationName = 'fbnotify',
			notifications = ['Errors', 'Notifications'],
			defaultNotifications = ['Errors', 'Notifications']
		)
		self.growl.register()

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
		self.growl.notify(
			noteType = 'Notifications',
			title = message['title'],
			description = message['body'],
			icon = message['icon_data'],
			callback = message['link'],
			sticky = False,
			priority = 1,
		)