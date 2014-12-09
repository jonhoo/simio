#! /usr/bin/env python2
import sys, os
import threading
import pygtk
pygtk.require('2.0')
import gtk, gobject
import pyinotify

f = None
img = None
class ProcessTransientFile(pyinotify.ProcessEvent):
	def update_img(self, p):
		img.set_from_file(f)
		return False

	def process_IN_CREATE(self, event):
		# We have explicitely registered for this kind of event.
		if event.pathname == f:
			gobject.idle_add(self.update_img, event.pathname)

	def process_default(self, event):
		pass

if __name__ == '__main__':
	gobject.threads_init()
	window = gtk.Window()
	window.connect("delete-event", gtk.main_quit)
	img = gtk.Image()
	img.set_from_file(sys.argv[1])
	img.show()
	window.add(img)
	window.present()

	f = os.path.abspath(sys.argv[1])

	wm = pyinotify.WatchManager()
	notifier = pyinotify.ThreadedNotifier(wm, ProcessTransientFile())
	notifier.start()
	wm.add_watch(os.path.dirname(sys.argv[1]), pyinotify.IN_CREATE)

	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	gtk.main()
	notifier.stop()
