Facebook Notifier
=================

**fbnotify** ~~is~~ will be a cross-platform Facebook notifier using Python. 

This is still in-development!

It runs in the background and notifies you whenever you get a notification in Facebook. Notifications come to you instead of you coming for them.

Installation
------------

Simply copy everything to any directory.

You need to configure it to listen to your Facebook notifications feed.

First, execute `fbnotify.py`. It will show an error saying 'no url found'. This URL is your FB feed. To get this URL:
1. Go to www.facebook.com/notifications.
2. Copy the RSS link.
3. Open the configuration file. (See the terminal output for the path. This is usually at `~/.config/fbnotify/fbnotify.conf`.)
4. Paste the URL to the `url` field in the `[feed]` section.

Usage
-----

To run, execute `fbnotify.py`.

To stop, use an interrupt signal `^C`.

Plugins
-------

There is a plugin system to aid in making it cross-platform.

* pynotify
	Plugin to handle notifications using libnotify.
* Growl
	**UNTESTED** Plugin for showing notifications using Growl
* PyGTK
	Plugin for displaying a status icon in the notification area
* Unity_indicator
	Plugin for displaying an app indicator for Unity

### Not Yet Implemented ###

* Unity Messaging Menu plugin
* GTK status icon notifications (not libnotify)
* Windows notifications
* Windows status icon

Libraries
=========

Libraries included are listed here. Files are listed as well.

* [ActiveState/appdirs](https://github.com/ActiveState/appdirs) to get configuration directory
	* appdirs.py
	* appdirs.pyc
* [borntyping/python-colorlog](https://github.com/borntyping/python-colorlog) for colorful logging
	* colorlog/colorlog.py
	* colorlog/escape_codes.py

License
=======

This software is released under the **GNU General Public License** (GPL) which
can be found in the file **LICENSE** in the same directory as this file.

Licenses for the included libraries can be found in the same directory in the files **_name_.LICENSE** where _name_ is the name of the library.