from item import Item

import webbrowser
from threading import Thread


# Try to import libraries
#
# Notification: pynotify, Growl, gntp
# Indicator:    PyGTK
# GUI:          wxPython
# 
pynotify = Growl = gntp = gtk = wx = None


# Notification
# ============
loaded = False

# pynotify (Linux)
if not loaded:
	try:
		import pynotify
		loaded = True
		print('Loaded pynotify')
	except ImportError:
		pass

# Growl (Mac)
if not loaded:
	try:
		import Growl
		loaded = True
		print('Loaded Growl')
	except ImportError:
		pass

# gntp (Growl - Mac)
if not loaded:
	try:
		import gntp
		loaded = True
		print('Loaded gntp')
	except ImportError:
		pass


# Indicator
# =========
loaded = False

# GTK (Cross plaform)
if not loaded:
	try:
		import gtkx
		import gobject
		loaded = True
		print('Loaded PyGTK')
	except ImportError:
		pass

# wx (Cross platform)
if not loaded:
	try:
		import wx
		loaded = True
		print('Loaded wxPython')
	except ImportError:
		pass


# User Interface
# ==============
loaded = False

# wx (Cross platform)
if not loaded and not wx:
	try:
		import wx
		loaded = True
		print('Loaded wx')
	except ImportError:
		wx = None

print('')


# System Notification
class SysNotif:
	def __init__(self, app_name, xdg_icon, icon_path):
		self.app_name = app_name
		self.link = None
		self.items = []
		self.xdg_icon = xdg_icon
		self.icon_path = icon_path

		self.growl = None
		self.gntp_notifier = None
		self.gtk_notif = None
		self.gtk_thread = None
		self.wx_notif = None
		self.wx_app = None
		self.wx_thread = None

		# Initialize notification library
		if pynotify:
			self._init_pynotify()
		elif Growl:
			self._init_Growl()
		elif gntp:
			self._init_gntp()

		# Initialize indicator library
		if gtk:
			self._init_gtk()
		elif wx:
			self._init_wx_notif()

		# Initialize GUI library
		if wx:
			self._init_wx_app()

		# Start main loops
		if gtk:
			gobject.threads_init()
			self.gtk_thread = Thread(target=gtk.main)
			self.gtk_thread.daemon = True;
			self.gtk_thread.start()
		if wx:
			self.wx_thread = Thread(target=self.wx_app.MainLoop)
			self.wx_thread.daemon = True;
			self.wx_thread.start()


	def _init_pynotify(self):
		print('Init pynotify')
		pynotify.init(self.app_name)

	def _init_Growl(self):
		print('Init Growl.GrowlNotifier')
		icon = {'applicationIcon': Growl.Image.imageFromPath(self.icon_path)}
		self.growl = Growl.GrowlNotifier(self.app_name, [self.app_name], **icon)

	def _init_gntp(self):
		print('Init gntp,notifier.GrowlNotifier')
		self.gntp_notifier = gntp.notifier.GrowlNotifier(
			applicationName = self.app_name,
			notifications = ['New Notifications'],
			defaultNotifications = ['New Notifications'],
		)
		self.gntp_notifier.register()

	def _init_gtk(self):
		# Create status icon in notification area
		print('Init gtk.StatusIcon')
		self.gtk_notif = si = gtk.StatusIcon()
		si.set_from_icon_name('facebook')
		si.set_visible(True)
		si.connect('popup-menu', self.gtk_popup_menu)

	def _init_wx_notif(self):
		# Create wx.App
		if not self.wx_app:
			print('Init wx.App')
			self.wx_app = wx.App(False)

		# Create status icon in notification area
		print('Init wx.TaskBarIcon')
		self.wx_notif = si = wx.TaskBarIcon()
		si.SetIcon(wx.IconFromBitmap(wx.Bitmap(self.icon_path)), self.app_name)
		si.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.wx_popup_menu)


	def _init_wx_app(self):
		# Create wx.App
		if not self.wx_app:
			print('Init wx.App')
			self.wx_app = wx.App(False)


	############################################################################
	# Application functions
	############################################################################

	def stop(self):
		# Stop main loops
		if gtk:
			gtk.main_quit()
		if self.wx_notif:
			self.wx_notif.Destroy()
			self.wx_notif = None


	def send(self, title, message, urgency=None, timeout=None):
		if pynotify:

			n = pynotify.Notification(title, message, self.xdg_icon)
			if urgency:
				n.set_urgency(getattr(pynotify, 'URGENCY_%s' % urgency.upper()))
			if timeout:
				n.set_timeout(timeout)
			n.show()

		elif Growl:

			self.growl.notify('fbnotify', title, message)

		elif gntp:

			self.gntp_notifier.notify(
				noteType = "New Notifications",
				title = title,
				description = message,
				icon = "http://example.com/icon.png",
				sticky = False,
				priority = 1,
			)

		elif self.wx_notif.ShowBalloon:

			if not timeout:
				timeout = 10

			self.wx_notif.ShowBalloon(self, title, message, timeout * 1000)

	def add_items(self, items):
		self.items.extend(reversed(items))
		del self.items[10:]

	def set_tooltip(self, text):
		if gtk:
			self.gtk_notif.set_tooltip(text)

	############################################################################
	# Menu actions
	############################################################################

	def open_website(self):
		webbrowser.open('www.facebook.com/notifications', 2)

	def open_url(self, url):
		webbrowser.open(url, 2)

	def show_about_dialog(self):
		if wx:
			about_info = wx.AboutDialogInfo()

			about_info.SetName('fbnotify')
			#about_info.SetVersion('0.0.0')
			about_info.SetDescription('fbnotify is a notifier for Facebook notifications')
			about_info.AddDeveloper('Lean Rada')

			wx.AboutBox(about_info)
	
	def menu_quit(self):
		self.stop()
		quit()

	############################################################################
	# Popup menu
	############################################################################

	def gtk_popup_menu(self, icon, button, time):
		menu = gtk.Menu()

		if self.items:
			for item in self.items:
				menu_item = gtk.MenuItem(item.text)
				menu_item.connect('activate', lambda w: self.open_website(item.link))
				menu.append(menu_item)
		else:
			blank_item = gtk.MenuItem('No new notifications')
			blank_item.set_sensitive(False)
			menu.append(blank_item)
		menu.append(gtk.SeparatorMenuItem())

		go_item = gtk.MenuItem('Launch Facebook Website')
		about_item = gtk.MenuItem('About')
		quit_item = gtk.MenuItem('Quit')

		menu.append(go_item)
		menu.append(about_item)
		menu.append(quit_item)

		go_item.connect('activate', lambda w: self.open_website())
		about_item.connect('activate', lambda w: self.show_about_dialog())
		quit_item.connect('activate', lambda w: self.menu_quit())

		menu.show_all()
		menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.gtk_notif)

	def wx_popup_menu(self, event):
		menu = wx.Menu()

		if self.items:
			for item in self.items:
				item = wx.MenuItem(menu, wx.NewId(), item.text)
				menu.AppendItem(item)
				menu.Bind(wx.EVT_MENU, lambda e: webbrowser.open(item.link, 2), id=item.GetId())
		else:
			blank_item = wx.MenuItem(menu, wx.NewId(), 'No new notifications')
			menu.AppendItem(blank_item)
			blank_item.Enable(False)
		menu.AppendSeparator()

		go_item = wx.MenuItem(menu, wx.NewId(), 'Launch Facebook Website')
		about_item = wx.MenuItem(menu, wx.NewId(), 'About')
		quit_item = wx.MenuItem(menu, wx.NewId(), 'Quit')

		menu.AppendItem(go_item)
		menu.AppendItem(about_item)
		menu.AppendItem(quit_item)

		menu.Bind(wx.EVT_MENU, lambda e: self.open_website(), id=go_item.GetId())
		menu.Bind(wx.EVT_MENU, lambda e: self.show_about_dialog(), id=about_item.GetId())
		menu.Bind(wx.EVT_MENU, lambda e: self.menu_quit(), id=quit_item.GetId())

		self.wx_notif.PopupMenu(menu)
