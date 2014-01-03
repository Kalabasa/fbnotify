from PluginBase import PluginBase

import gtk
gtk.gdk.threads_init()
import gobject

class Plugin(PluginBase):
	''' provides status icon in the notification area '''

	icon = None
	items = []

	def plugin_init(self):
		# Create a StatusIcon
		self.icon = gtk.StatusIcon()
		self.icon.set_from_icon_name('facebook')
		self.icon.set_tooltip('fbnotify')
		self.icon.set_visible(True)

		# Respond to clicks
		self.icon.connect('popup-menu', self.popup_menu)

		# Poll messages periodically
		gobject.timeout_add_seconds(1, self.timer_call)

		# Start gtk main loop
		gtk.main()

	def plugin_destroy(self):
		# Stop gtk
		gtk.main_quit()

	def plugin_receive(self, channel, message):
		# Receive and react
		if channel == 'list':
			self.list(message)
		elif channel == 'indicate':
			self.indicate(message)
			
	def timer_call(self):
		# Call context.receive() to receive messages
		self.context.receive()
		return True

	def list(self, message):
		self.items.extend(message['items'])
		del self.items[10:]

	def indicate(self, message):
		pass

	def popup_menu(self, icon, button, time):
		menu = gtk.Menu()

		for i in self.items:
			menu_item = gtk.MenuItem(i.text)
			menu.append(menu_item)

		menu.show_all()

		menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.icon)