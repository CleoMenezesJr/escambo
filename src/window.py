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

import json
import os
import re

from getoverhere.populator_entry import PupulatorEntry
from getoverhere.restapi import ResolveRequests
from gi.repository import Adw, Gio, GLib, Gtk
from requests import Session

COOKIES = os.path.join(GLib.get_user_config_dir(),
                       "getoverhere", "cookies.json")


@Gtk.Template(resource_path="/io/github/cleomenezesjr/GetOverHere/window.ui")
class GetoverhereWindow(Adw.ApplicationWindow):
    __gtype_name__ = "GetoverhereWindow"

    # Template objects
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
    # btn_send_reques = Gtk.Template.Child()

    entry_cookie_key = Gtk.Template.Child()
    entry_cookie_value = Gtk.Template.Child()
    btn_add_cookie = Gtk.Template.Child()
    group_overrides = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.kwargs = kwargs
        # Ensure close session
        with Session() as session:
            self.session = session

        # Connect signals
        self.btn_send_request.connect("clicked", self.__on_send)
        self.btn_go_back.connect("clicked", self.__go_back)
        self.btn_raw_go_back.connect("clicked", self.__go_back, True)
        self.btn_edit_param.connect("activated", self.__on_edit_param)
        self.payload = None
        self.is_raw_query_type = False
        self.raw_toggle_button.connect(
            "clicked", self.__which_query_type, True)
        self.form_data_toggle_button.connect(
            "clicked", self.__which_query_type, False)

        self.__populate_overrides_list()
        self.cookies = {}

        self.btn_add_cookie.connect("clicked", self.__save_override)

        # GSettings object
        self.settings = Gio.Settings.new("io.github.cleomenezesjr.GetOverHere")

    def __on_send(self, *_args):
        """
        This function checks if the submitted URL is validself.

        If validated, it proceeds to generate the request,
        otherwise it returns a Toast informing that the URL
        is using bad/illegal format or that it is missing.
        """
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
                    Adw.Toast.new(
                        ("URL using bad/illegal format or missing URL"))
                )
            else:
                self.__which_method(method, url)

    def __which_method(self, selected, url):
        match selected:
            case 0:
                buffer = self.response_text.get_buffer()
                buffer.set_text(
                    ResolveRequests(
                        url,
                        self.session,
                        cookies=self.cookies,
                        payload=self.payload,
                    ).resolve_get()
                )
                self.leaflet.set_visible_child(self.response_page)
            case 1:
                buffer = self.response_text.get_buffer()
                response = ResolveRequests(
                    url,
                    self.session,
                    payload=self.payload,
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
        """
        Returns to main leaf regardless
        of how many leaves the front is
        """
        if any(x for x in _args if x is True):
            buffer = self.raw_text.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            self.payload = buffer.get_text(start_iter, end_iter, True)

        self.leaflet.set_visible_child(self.home)

    def __save_override(self, *_args):
        """
        This function check if the override name is not empty, then
        store it in the bottle configuration and add a new entry to
        the list. It also clears the entry field
        """
        cookie_key = self.entry_cookie_key.get_text()
        cookie_value = self.entry_cookie_value.get_text()

        if cookie_key != "" and cookie_value != "":
            json_cookie = json.dumps({cookie_key: cookie_value}, indent=2)
            _entry = PupulatorEntry(
                window=self,
                override=[cookie_key, cookie_value],
                cookies=COOKIES,
            )
            GLib.idle_add(self.group_overrides.add, _entry)

            # Save cookies
            if not os.path.exists(COOKIES):
                os.makedirs(os.path.dirname(COOKIES), exist_ok=True)
                with open(COOKIES, "w") as file:
                    file_content = file.write(json_cookie)
            else:
                with open(COOKIES, "r+") as file:
                    file_content = json.load(file)
                    file_content.update({cookie_key: cookie_value})
                    file.seek(0)
                    json.dump(file_content, file, indent=2)

            self.cookies = file_content

            # Clean up fields
            self.group_overrides.set_description("")
            self.entry_cookie_key.set_text("")
            self.entry_cookie_value.set_text("")

    def __populate_overrides_list(self):
        """
        This function populate the list of cookies
        """
        if os.path.exists(COOKIES):
            with open(COOKIES, "r") as file:
                overrides = json.load(file)
                overrides = dict(reversed(list(overrides.items())))
                if not bool(overrides):
                    self.group_overrides.set_description(("No cookie added."))
                else:
                    self.cookies = overrides
                    self.group_overrides.set_description("")
                    for override in overrides:
                        _entry = PupulatorEntry(
                            window=self,
                            override=[override, overrides[override]],
                            cookies=COOKIES,
                        )
                        GLib.idle_add(self.group_overrides.add, _entry)
