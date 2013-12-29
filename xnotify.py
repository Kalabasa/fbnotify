from item import Item

import webbrowser

try:
	import pynotify
except ImportError:
	pynotify = None

try:
	import gtk
	import gobject
	gobject.threads_init()
except ImportError:
	gtk = None

from threading import Thread

class SysNotif:
	def __init__(self, app_name):
		# Initialize notification library
		pynotify.init(app_name)
		self.app_name = app_name
		self.link = None
		self.items = []

		if gtk:
			self._init_gtk()

	def _init_gtk(self):
		# Create status icon in notification area
		self.gtk_notif_icon = si = gtk.StatusIcon()
		si.set_from_icon_name('facebook')
		si.set_visible(True)
		si.connect('activate', self.gtk_activate)
		si.connect('popup-menu', self.gtk_popup_menu)

		# Start gtk.main
		self.gtk_thread = Thread(target=gtk.main)
		self.gtk_thread.daemon = True
		self.gtk_thread.start()

	def stop(self):
		if gtk:
			gtk.main_quit()
			self.gtk_thread.join()

	def send(self, title, message, icon=None, wxicon=None, urgency=None, timeout=None):
		if pynotify:
			n = pynotify.Notification(title, message, icon)
			if urgency:
				n.set_urgency(getattr(pynotify, 'URGENCY_%s' % urgency.upper()))
			if timeout:
				n.set_timeout(timeout)
			n.show()

	def add_items(self, items):
		self.items.extend(reverse(items))
		del self.items[10:]

	def set_tooltip(self, text):
		if gtk:
			self.gtk_notif_icon.set_tooltip(text)
	
	if gtk:
		def gtk_activate(self, icon):
			return

		def gtk_popup_menu(self, icon, button, time):
			menu = gtk.Menu()

			if self.items:
				for item in self.items:
					menu_item = gtk.MenuItem(item.text)
					menu.append(menu_item)
				menu.append(gtk.SeparatorMenuItem())

			go_item = gtk.MenuItem("Launch Facebook Website")
			about_item = gtk.MenuItem("About")
			quit_item = gtk.MenuItem("Quit")

			menu.append(go_item)
			menu.append(about_item)
			menu.append(quit_item)

			menu.show_all()

			menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.gtk_notif_icon)