# This file is part of fbnotify
#
# Copyright (c) 2014 Lean Rada <godffrey0@gmail.com>
# 
# fbnotify is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# fbnotify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with fbnotify.  If not, see <http://www.gnu.org/licenses/>.

import notices
from PluginBase import PluginBase
import icons

import gtk
import gobject
import appindicator

import webbrowser
import textwrap
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
		if channel == 'list':
			self.list(message)
		elif channel == 'status':
			self.status(message)

	def list(self, message):
		new_items = sorted(message['items'], key=lambda x: x.dt)
		self.items = self.items + new_items
		del self.items[:-10]
		self.update_menu()

	def status(self, message):
		if message['status'] == 'error':
			

	def update_menu(self):
		menu = gtk.Menu()

		if self.items:
			for i in self.items:
				menu_item = gtk.ImageMenuItem(i.wrapped)

				def get_callback(item):
					def f(widget):
						webbrowser.open(item.link)
					return f
				menu_item.connect('activate', get_callback(i))

				if i.image_path:
					item_image = gtk.Image()
					item_image.set_from_file(i.image_path)
					menu_item.set_image(item_image)

				menu.append(menu_item)
		else:
			msg = gtk.MenuItem('No Notifications')
			msg.set_sensitive(False)
			menu.append(msg)

		menu.append(gtk.SeparatorMenuItem())

		clear = gtk.ImageMenuItem(gtk.STOCK_CLEAR)
		refresh = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
		launch = gtk.ImageMenuItem('Launch Facebook Website')
		launch_image = gtk.Image()
		launch_image.set_from_stock(gtk.STOCK_HOME, 22)
		launch.set_image(launch_image)
		about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)

		clear.connect('activate', self.menu_clear)
		refresh.connect('activate', self.menu_refresh)
		launch.connect('activate', self.menu_launch)
		about.connect('activate', self.menu_about)
		quit.connect('activate', self.menu_quit)

		menu.append(clear)
		menu.append(refresh)
		menu.append(launch)
		menu.append(gtk.SeparatorMenuItem())
		menu.append(about)
		menu.append(quit)

		clear.set_sensitive(bool(self.items))

		menu.show_all()

		self.indicator.set_menu(menu)

	def menu_clear(self, widget):
		del self.items[:]
		self.update_menu()

	def menu_refresh(self, widget):
		self.context.send('fbnotify', refresh=True)

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