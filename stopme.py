import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import psutil
import threading
import time
import os

BLOCKED_APPS_FILE = os.path.join(os.environ['SNAP'], 'blocked_apps.txt')

class StopMeApp(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("StopMe - Focus Mode")
        self.set_default_size(320, 120)

        self.focus_active = False
        self.thread = None

        # Layout using Gtk.Box (replacement for VBox)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        self.set_child(vbox)

        # Status label
        self.status_label = Gtk.Label(label="Focus mode is OFF")
        vbox.append(self.status_label)

        # Toggle button
        self.toggle_button = Gtk.Button(label="Start Focus Mode")
        self.toggle_button.connect("clicked", self.toggle_focus_mode)
        vbox.append(self.toggle_button)

    def toggle_focus_mode(self, button):
        if self.focus_active:
            self.focus_active = False
            self.status_label.set_text("Focus mode is OFF")
            self.toggle_button.set_label("Start Focus Mode")
        else:
            self.focus_active = True
            self.status_label.set_text("Focus mode is ON")
            self.toggle_button.set_label("Stop Focus Mode")
            self.thread = threading.Thread(target=self.monitor_apps, daemon=True)
            self.thread.start()

    def monitor_apps(self):
        blocked_apps = self.load_blocked_apps()
        while self.focus_active:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in blocked_apps:
                    try:
                        proc.kill()
                        print(f"Killed: {proc.info['name']}")
                    except Exception as e:
                        print(f"Error killing {proc.info['name']}: {e}")
            time.sleep(2)

    def load_blocked_apps(self):
        try:
            with open(BLOCKED_APPS_FILE, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            return set()

class StopMe(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='stopme')

    def do_activate(self):
        win = StopMeApp(self)
        win.present()

def main():
    app = StopMe()
    app.run(None)

if __name__ == "__main__":
    main()
