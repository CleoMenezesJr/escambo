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
from requests import Session


@Gtk.Template(resource_path="/io/github/cleomenezesjr/GetOverHere/window.ui")
class GetoverhereWindow(Adw.ApplicationWindow):
    __gtype_name__ = "GetoverhereWindow"

    toast_overlay = Gtk.Template.Child()
    leaflet = Gtk.Template.Child()

    entry_method = Gtk.Template.Child()
    entry_url = Gtk.Template.Child()

    response_page = Gtk.Template.Child()
    raw_page = Gtk.Template.Child()
    response_text = Gtk.Template.Child()
    raw_text = Gtk.Template.Child()

    btn_go_back = Gtk.Template.Child()
    btn_raw_go_back = Gtk.Template.Child()
    btn_edit_param = Gtk.Template.Child()

    form_data_toggle_button = Gtk.Template.Child()
    raw_toggle_button = Gtk.Template.Child()
    home = Gtk.Template.Child()

    btn_send_request = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with Session() as session:
            self.session = session
        self.btn_send_request.connect("clicked", self.__on_send)
        self.btn_go_back.connect("clicked", self.__go_back)
        self.btn_raw_go_back.connect("clicked", self.__go_back, True)
        self.btn_edit_param.connect("activated", self.__on_edit_param)
        self.post_parameters = None
        self.is_raw_query_type = False
        self.raw_toggle_button.connect(
            "clicked",
            self.__which_query_type,
            True
        )
        self.form_data_toggle_button.connect(
            "clicked",
            self.__which_query_type,
            False
        )
        # print(dir(self.btn_edit_param.connect()))
        # self.raw_toggle_button.connect("clicked", self.__go_back)
        # print(dir(self.query_type))
        # print(self.query_type.get_focusable())
        # self.response_page.connect("insert-text", self.eita)

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
        match selected:
            case 0:
                buffer = self.response_text.get_buffer()
                buffer.set_text(
                    ResolveRequests(url, self.session).resolve_get()
                )
                self.leaflet.set_visible_child(self.response_page)
            case 1:
                payload = self.post_parameters
                buffer = self.response_text.get_buffer()
                response = ResolveRequests(
                    url,
                    self.session,
                    payload,
                ).resolve_post()
                buffer.set_text(response)
                self.leaflet.set_visible_child(self.response_page)

    def __which_query_type(self, *_args):
        status = any(x for x in _args if x is True)
        self.is_raw_query_type = status

    def __on_edit_param(self, *_args):
        if self.is_raw_query_type:
            self.leaflet.set_visible_child(self.raw_page)

    def __go_back(self, *_args):
        if any(x for x in _args if x is True):
            buffer = self.raw_text.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            self.post_parameters = buffer.get_text(start_iter, end_iter, True)

        self.leaflet.set_visible_child(self.home)
