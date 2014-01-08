import notices
from PluginBase import PluginBase

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import webbrowser
import time


class Plugin(PluginBase):
	''' provides status icon in the notification area '''

	running = False
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
		self.running = True
		while self.context and self.running:
			self.context.receive()
			time.sleep(1)

	def plugin_destroy(self):
		self.running = False

	def plugin_receive(self, channel, message):
		# Receive 'list' message
		self.list(message)

	def list(self, message):
		new_items = sorted(message['items'], key=lambda x: x.dt)
		self.items = self.items + new_items
		del self.items[:-10]

	def popup_menu(self, icon, button, time):
		menu = gtk.Menu()

		if self.items:
			for i in self.items:
				menu_item = gtk.MenuItem(i.text)
				def get_callback(item):
					def f(widget):
						webbrowser.open(item.link)
					return f
				menu_item.connect('activate', get_callback(i))
				menu.append(menu_item)
		else:
			msg = gtk.MenuItem('No Notifications')
			msg.set_sensitive(False)
			menu.append(msg)

		menu.append(gtk.SeparatorMenuItem())

		launch = gtk.MenuItem('Launch Facebook Website')
		about = gtk.MenuItem('About')
		quit = gtk.MenuItem('Quit')

		launch.connect('activate', self.menu_launch)
		about.connect('activate', self.menu_about)
		quit.connect('activate', self.menu_quit)

		menu.append(about)
		menu.append(quit)

		menu.show_all()

		menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.icon)

	def menu_launch(self, widget):
		webbrowser.open('www.facebook.com')

	def menu_about(self, widget):
		about_dialog = gtk.AboutDialog()

		about_dialog.set_destroy_with_parent(True)
		about_dialog.set_name(notices.name)
		about_dialog.set_version(notices.version)
		about_dialog.set_comments(notices.description)
		about_dialog.set_copyright(notices.copyright)
		about_dialog.set_authors(notices.authors)
		about_dialog.set_license(notices.license)
		
		about_dialog.run()
		about_dialog.destroy()

	def menu_quit(self, widget):
		self.icon.set_visible(False)
		self.context.send('fbnotify', quit=True)