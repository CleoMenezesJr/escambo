# main.py
#
# Copyright 2022 Cleo Menezes Jr.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GtkSource", "5")

from gi.repository import Adw, Gio, Gtk

from .window import EscamboWindow


class EscamboApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="io.github.cleomenezesjr.Escambo",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.create_action("quit", self.quit, ["<primary>q"])
        self.create_action("about", self.on_about_action)
        # self.create_action("preferences", self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = EscamboWindow(application=self)
        win.present()

        self.setup_escambo_actions(win)

    def setup_escambo_actions(self, win):
        self.create_action(
            "on_send", win._EscamboWindow__on_send, ["<primary>Return"]
        )
        self.create_action(
            "show-response",
            win._EscamboWindow__set_response_visibility,
            ["<primary>r"],
        )

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name=_("Escambo"),
            application_icon="io.github.cleomenezesjr.Escambo",
            developer_name="Cleo Menezes Jr.",
            version="0.1.1",
            developers=["Cleo Menezes Jr. https://github.com/CleoMenezesJr"],
            copyright="© 2022 Cleo Menezes Jr.",
            comments=_("An HTTP-based APIs test application for GNOME."),
            license_type=Gtk.License.GPL_3_0,
            issue_url="https://github.com/CleoMenezesJr/escambo/issues/new",
            support_url="https://ko-fi.com/cleomenezesjr",
            icon_name="Escambo",
        )
        about.present()

    # def on_preferences_action(self, widget, _):
    #     """Callback for the app.preferences action."""
    #     print("app.preferences action activated")

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = EscamboApplication()
    return app.run(sys.argv)
