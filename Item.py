class Item:
	''' a notification item '''

	text = ''
	link = ''
	dt = None

	def __init__(self, text, link, dt):
		self.text = text
		self.link = link
		self.dt = dt