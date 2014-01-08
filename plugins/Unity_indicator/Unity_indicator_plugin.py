import notices
from PluginBase import PluginBase
import icons

import gtk
import gobject
import appindicator

import webbrowser
import time


class Plugin(PluginBase):
	''' provides an app indicator icon for Unity '''

	running = False
	indicator = None
	items = []

	def plugin_init(self):
		# Create the indicator
		self.indicator =  appindicator.Indicator('fbnotify', icons.icon_path, appindicator.CATEGORY_APPLICATION_STATUS)
		self.indicator.set_status(appindicator.STATUS_ACTIVE)
		self.indicator.set_attention_icon(icons.icon_new_path)

		self.update_menu()

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

		self.indicator.set_status(appindicator.STATUS_ATTENTION)
		self.update_menu()

	def update_menu(self):
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

		clear = gtk.MenuItem('Clear')
		launch = gtk.MenuItem('Launch Facebook Website')
		about = gtk.MenuItem('About')
		quit = gtk.MenuItem('Quit')

		clear.connect('activate', self.menu_clear)
		launch.connect('activate', self.menu_launch)
		about.connect('activate', self.menu_about)
		quit.connect('activate', self.menu_quit)

		menu.append(clear)
		menu.append(launch)
		menu.append(about)
		menu.append(quit)

		menu.show_all()

		self.indicator.set_menu(menu)

	def menu_clear(self, widget):
		del items[:]
		self.indicator.set_status(appindicator.STATUS_ACTIVE)
		self.update_menu()

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
		self.indicator.set_status(appindicator.STATUS_PASSIVE)
		self.context.send('fbnotify', quit=True)