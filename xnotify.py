from item import Item
import webbrowser

# Try to import libraries
pynotify = Growl = gntp = None
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


# System Notification
class SysNotif:
	def __init__(self, app_name, xdg_icon, icon_path):
		self.app_name = app_name
		self.xdg_icon = xdg_icon
		self.icon_path = icon_path
		self.icon_data = open(icon_path, 'rb').read()

		# Initialize notification library
		if pynotify:
			self._init_pynotify()
		elif Growl:
			self._init_Growl()
		elif gntp:
			self._init_gntp()


	def _init_pynotify(self):
		pynotify.init(self.app_name)

	def _init_Growl(self):
		icon = {'applicationIcon': Growl.Image.imageFromPath(self.icon_path)}
		self.growl = Growl.GrowlNotifier(self.app_name, [self.app_name], **icon)

	def _init_gntp(self):
		self.gntp_notifier = gntp.notifier.GrowlNotifier(
			applicationName = self.app_name,
			notifications = ['New Notifications'],
			defaultNotifications = ['New Notifications'],
		)
		self.gntp_notifier.register()


	if pynotify:
		def send(self, title, message, urgency=None, timeout=None):
			n = pynotify.Notification(title, message, self.xdg_icon)
			if urgency:
				n.set_urgency(getattr(pynotify, 'URGENCY_%s' % urgency.upper()))
			if timeout:
				n.set_timeout(timeout)
			n.show()

	elif Growl:
		def send(self, title, message, urgency=None, timeout=None):
			self.growl.notify('fbnotify', title, message)

	elif gntp:
		def send(self, title, message, urgency=None, timeout=None):
			self.gntp_notifier.notify(
				noteType = "New Notifications",
				title = title,
				description = message,
				icon = self.icon_data,
				sticky = False,
				priority = 1,
			)

	else:
		def send(self, title, message, urgency=None, timeout=None):
			pass