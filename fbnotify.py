#!/usr/bin/env python

import notices
from Notifier import Notifier

import colorlog

import logging

if __name__ == '__main__':
	# Setup logger
	fh = logging.FileHandler('fbnotify.log')
	sh = logging.StreamHandler()
	formatter = colorlog.ColoredFormatter(
		"%(log_color)s[%(name)s] %(levelname)-8s %(message)s%(reset)s",
		datefmt=None,
		reset=True,
		log_colors={
			'DEBUG':    'cyan',
			'WARNING':  'yellow',
			'ERROR':    'red',
			'CRITICAL': 'bold_red',
		}
	)
	sh.setFormatter(formatter)
	
	root = logging.getLogger('')
	root.addHandler(fh)
	root.addHandler(sh)
	root.setLevel(logging.DEBUG)

	# Credits!
	print(notices.license)

	# Start!
	Notifier().start()
