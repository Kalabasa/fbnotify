Facebook Notifier
=================

**fbnotify** ~~is~~ will be a cross-platform Facebook notifier using Python. 

This is still in-development!

It runs in the background and notifies you whenever you get a notification in Facebook. Notifications come to you instead of you coming for them.

[fbnotify notification screenshot](http://i.imgur.com/OFotbMk.png 'Desktop notification')

[fbnotify status icon screenshot](http://i.imgur.com/05dtT1K.png 'Status icon shows up in the panel')

Setup
-----

Copy everything to any directory.

You need to configure it to listen to your Facebook notifications feed.

First, execute `fbnotify.py`. It will show an error saying `no url found`. This URL, which is your FB feed, is needed by the program.

To get this URL:

	1. Go to www.facebook.com/notifications.
	2. Copy the **RSS** link in the **Get notifications via:** part.
	3. Open the configuration file. See the terminal output for the path. This is usually at `~/.config/fbnotify/fbnotify.conf`
	4. Paste the URL to the `url` field in the `[feed]` section.

Usage
-----

To run, execute `fbnotify.py`. It is supposed to be ran in the background.

To stop, use an interrupt signal `^C` and wait for it to finish.

Configuration
-------------

`~/.config/fbnotify/fbnotify.conf`

*TODO*

Plugins
-------

There is a plugin system. Plugins are responsible for showing notifications, responding to things, etc. They are the frontend of the program.

* pynotify - shows notifications using libnotify.
* Growl - shows notifications using Growl. (**UNTESTED!**)
* PyGTK - displays a status icon in the notification area
* Unity_indicator - displays an indicator in Unity
* gtk_base - needed by some plugins

Plugins are located in the `plugins/` directory or in `~/.config/fbnotify/plugins/` or similar.

### Not Yet Implemented ###

* Unity Messaging Menu
* GTK status icon notifications (not libnotify)
* Mac status icon (?)
* Mac notifications (?)
* Windows notifications
* Windows status icon

Libraries
=========

Libraries included are listed here. Files are listed as well.

* [ActiveState/appdirs](https://github.com/ActiveState/appdirs) to get configuration directory
	* appdirs.py
* [borntyping/python-colorlog](https://github.com/borntyping/python-colorlog) for colorful logging
	* colorlog/colorlog.py
	* colorlog/escape_codes.py

License
=======

This software is released under the **GNU General Public License** (GPL) which
can be found in the file **LICENSE** in the same directory as this file.

Licenses for the included libraries can be found in the same directory in the files **_{name}_.LICENSE** where _{name}_ is the name of the library.