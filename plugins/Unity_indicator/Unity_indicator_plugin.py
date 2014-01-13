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

from datetime import datetime
import webbrowser
import time


class Plugin(PluginBase):
	''' provides an app indicator icon for Unity '''

	running = False

	indicator = None
	menu = None
	menu_notif_items = []
	menu_handlers = []

	items = []
	has_new_items = False
	max_items = 10

	status = None
	message = None
	last_refresh = None

	def plugin_init(self):
		# Create the indicator
		self.indicator =  appindicator.Indicator('fbnotify', icons.icon_path, appindicator.CATEGORY_APPLICATION_STATUS)
		self.indicator.set_status(appindicator.STATUS_ACTIVE)
		self.indicator.set_attention_icon(icons.icon_new_path)

		self.create_menu()
		self.update_menu()

		# Wait for context
		while not self.context:
			pass

		# Poll messages periodically
		count = 1
		self.running = True
		while self.running:
			self.context.receive()

			# Animate when updating
			if self.status == 'updating':
				self.indicator.set_icon(icons.icon_updating_paths[count])
				count = 0 if count == 4 else count + 1

				if count == 1:
					time.sleep(0.3)
				time.sleep(0.1)
			else:
				time.sleep(1)

	def plugin_destroy(self):
		self.menu.popdown()
		self.running = False

	def plugin_receive(self, channel, message):
		if channel == 'list':
			self.list(message)
		elif channel == 'status':
			self.status_message(message)

	def list(self, message):
		new_items = sorted(message['items'], key=lambda x: x.dt)
		self.items = self.items + new_items
		del self.items[:-self.max_items]
		self.has_new_items = True
		self.update_menu()

	def status_message(self, message):
		self.status = message['status']
		if self.status == 'idle':
			self.indicator.set_icon(icons.icon_path)
			self.message = None
		elif self.status == 'updating':
			self.indicator.set_icon(icons.icon_updating_paths[0])
			self.last_refresh = datetime.now()
		elif self.status == 'error':
			self.indicator.set_icon(icons.icon_error_path)
			self.message = message['description']
		self.update_menu()

	def create_menu(self):
		menu = gtk.Menu()

		for i in range(0,self.max_items):
			menu_item = gtk.ImageMenuItem('Notification')
			menu.append(menu_item)
			self.menu_notif_items.append(menu_item)
			self.menu_handlers.append(None)

		self.msg_mi = gtk.MenuItem('No Notifications')
		self.msg_mi.set_sensitive(False)
		menu.append(self.msg_mi)

		menu.append(gtk.SeparatorMenuItem())

		self.clear_mi = gtk.ImageMenuItem(gtk.STOCK_CLEAR)
		self.refresh_mi = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
		self.launch_mi = gtk.ImageMenuItem('Launch Facebook Website')
		launch_image = gtk.Image()
		launch_image.set_from_stock(gtk.STOCK_HOME, gtk.ICON_SIZE_MENU)
		self.launch_mi.set_image(launch_image)
		self.about_mi = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		self.quit_mi = gtk.ImageMenuItem(gtk.STOCK_QUIT)

		self.clear_mi.connect('activate', self.menu_clear)
		self.refresh_mi.connect('activate', self.menu_refresh)
		self.launch_mi.connect('activate', self.menu_launch)
		self.about_mi.connect('activate', self.menu_about)
		self.quit_mi.connect('activate', self.menu_quit)

		menu.append(self.clear_mi)
		menu.append(self.refresh_mi)
		menu.append(self.launch_mi)
		menu.append(gtk.SeparatorMenuItem())
		menu.append(self.about_mi)
		menu.append(self.quit_mi)

		menu.show_all()
		for w in self.menu_notif_items:
			w.hide()

		self.menu = menu
		self.indicator.set_menu(menu)

	def update_menu(self):
		if self.has_new_items:
			index = len(self.menu_notif_items)
			for item in reversed(self.items):
				index -= 1
				menu_item = self.menu_notif_items[index]
				menu_item.set_label(item.wrapped)

				def get_callback(item):
					def f(widget):
						webbrowser.open(item.link)
					return f
				handler = self.menu_handlers[index]
				if handler:
					menu_item.disconnect(handler)
				handler = menu_item.connect('activate', get_callback(item))
				self.menu_handlers[index] = handler

				if item.image_path:
					item_image = gtk.Image()
					item_image.set_from_file(item.image_path)
					menu_item.set_image(item_image)

				menu_item.show()

			for i in range(0,index):
				self.menu_notif_items[i].hide()

		if self.message:
			self.msg_mi.set_label(self.message)
		elif self.last_refresh:
			self.msg_mi.set_label('Last Refresh ' + self.last_refresh.strftime('%X'))

		if bool(self.items):
			self.clear_mi.set_sensitive(True)
			self.clear_mi.set_label('Clear')
		else:
			self.clear_mi.set_sensitive(False)
			self.clear_mi.set_label('No Notifications')

		if self.status == 'updating':
			self.refresh_mi.set_sensitive(False)
			self.refresh_mi.set_label('Refreshing...')
		else:
			self.refresh_mi.set_sensitive(True)
			self.refresh_mi.set_label('Refresh')

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