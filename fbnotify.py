#!/usr/bin/env python

from Notifier import Notifier

import colorlog

import logging

if __name__ == '__main__':
	# Setup logger
	sh = logging.StreamHandler()
	formatter = colorlog.ColoredFormatter(
		"%(log_color)s[%(name)s] %(levelname)s: %(message)s%(reset)s",
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
	root.addHandler(sh)
	root.setLevel(logging.DEBUG)

	# Start!
	Notifier().start()
