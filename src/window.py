# window.py
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

import re

from gi.repository import Adw
from gi.repository import Gtk

from getoverhere.restapi import ResolveRequests


@Gtk.Template(resource_path="/io/github/cleomenezesjr/GetOverHere/window.ui")
class GetoverhereWindow(Adw.ApplicationWindow):
    __gtype_name__ = "GetoverhereWindow"

    entry_url = Gtk.Template.Child()
    btn_send_request = Gtk.Template.Child()
    entry_method = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    leaflet = Gtk.Template.Child()
    details_page = Gtk.Template.Child()
    src_text = Gtk.Template.Child()
    btn_go_back = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.btn_send_request.connect("clicked", self.__on_send)
        self.btn_go_back.connect("clicked", self.__go_back)

    def __on_send(self, *_args):
        regex = re.compile(
            r"^(?:http|ftp)s?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        url = self.entry_url.get_text()
        method = self.entry_method.get_selected()

        if not url:
            self.toast_overlay.add_toast(Adw.Toast.new(("Enter a URL")))
        else:
            if re.match(regex, url) is None:
                self.toast_overlay.add_toast(
                    Adw.Toast.new((
                        "URL using bad/illegal format or missing URL"
                    ))
                )
            else:
                self.__which_method(method, url)

    def __which_method(self, selected, url):
        if selected == 0:
            buffer = self.src_text.get_buffer()
            buffer.set_text(ResolveRequests(url).resolve_get())
            self.leaflet.set_visible_child(self.details_page)

    def __go_back(self, *_args):
        self.leaflet.navigate(Adw.NavigationDirection.BACK)
