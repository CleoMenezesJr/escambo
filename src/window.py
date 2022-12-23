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

# constants
COOKIES = os.path.join(GLib.get_user_config_dir(),
                       "getoverhere", "cookies.json")
PARAMETERS = os.path.join(GLib.get_user_config_dir(),
                          "getoverhere", "parameters.json")


@Gtk.Template(resource_path="/io/github/cleomenezesjr/GetOverHere/window.ui")
class GetoverhereWindow(Adw.ApplicationWindow):
    __gtype_name__ = "GetoverhereWindow"

    # Template objects
    toast_overlay = Gtk.Template.Child()
    leaflet = Gtk.Template.Child()

    entry_method = Gtk.Template.Child()
    entry_url = Gtk.Template.Child()

    response_page = Gtk.Template.Child()
    response_page_header = Gtk.Template.Child()
    raw_page = Gtk.Template.Child()
    form_data_page = Gtk.Template.Child()
    response_text = Gtk.Template.Child()
    raw_text = Gtk.Template.Child()

    btn_go_back = Gtk.Template.Child()
    btn_raw_go_back = Gtk.Template.Child()
    btn_form_data_go_back = Gtk.Template.Child()
    btn_edit_param = Gtk.Template.Child()

    form_data_toggle_button = Gtk.Template.Child()
    home = Gtk.Template.Child()

    btn_send_request = Gtk.Template.Child()

    entry_parameter_key = Gtk.Template.Child()
    entry_parameter_value = Gtk.Template.Child()
    btn_add_parameter = Gtk.Template.Child()
    group_overrides_parameter = Gtk.Template.Child()

    entry_cookie_key = Gtk.Template.Child()
    entry_cookie_value = Gtk.Template.Child()
    btn_add_cookie = Gtk.Template.Child()
    group_overrides_cookie = Gtk.Template.Child()

    cookie_page = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.kwargs = kwargs
        # Ensure close session
        with Session() as session:
            self.session = session

        # Connect signals
        self.btn_send_request.connect("clicked", self.__on_send)
        self.btn_edit_param.connect("activated", self.__on_edit_param)
        self.btn_add_cookie.connect("clicked", self.__save_override, "cookies")
        self.btn_add_parameter.connect(
            "clicked", self.__save_override, "parameters")

        self.btn_go_back.connect("clicked", self.__go_back)
        self.btn_raw_go_back.connect("clicked", self.__go_back)
        self.btn_form_data_go_back.connect("clicked", self.__go_back)

        # var
        self.cookies = {}
        self.parameters = {}

        self.__populate_overrides_list()

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
        parameter_type = self.form_data_toggle_button.props.active

        if not url:
            self.toast_overlay.add_toast(Adw.Toast.new(("Enter a URL")))
        else:
            if re.match(regex, url) is None:
                self.toast_overlay.add_toast(
                    Adw.Toast.new(
                        ("URL using bad/illegal format or missing URL"))
                )
            else:
                self.__which_method(method, url, parameter_type)

    def __which_method(self, method, url, parameter_type):

        if parameter_type:
            parameters = self.parameters
        else:
            buffer = self.raw_text.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            parameters = json.loads(
                buffer.get_text(start_iter, end_iter, True))

        buffer = self.response_text.get_buffer()
        match method:
            case 0:
                response, status_code = ResolveRequests(
                    url,
                    self.session,
                    cookies=self.cookies,
                    parameters=parameters,
                ).resolve_get()

                buffer.set_text(response)
            case 1:
                response, status_code = ResolveRequests(
                    url,
                    self.session,
                    cookies=self.cookies,
                    parameters=parameters,
                ).resolve_post()

        buffer.set_text(response)
        self.response_page_header.set_subtitle(str(status_code))
        self.leaflet.set_visible_child(self.response_page)

    def __on_edit_param(self, *_args):
        if not self.form_data_toggle_button.props.active:
            self.leaflet.set_visible_child(self.raw_page)
        else:
            self.leaflet.set_visible_child(self.form_data_page)

    def __go_back(self, *_args):
        self.leaflet.set_visible_child(self.home)

    def __save_override(self, *_args):
        """
        This function check if the override name is not empty, then
        store it in the configuration and add a new entry to
        the list. It also clears the entry field
        """
        match _args[1]:
            case "cookies":
                cookie_key = self.entry_cookie_key.get_text()
                cookie_value = self.entry_cookie_value.get_text()

                if cookie_key != "" and cookie_value != "":
                    json_cookie = json.dumps(
                        {cookie_key: cookie_value}, indent=2)
                    _entry = PupulatorEntry(
                        window=self,
                        override=[cookie_key, cookie_value],
                        content=COOKIES,
                    )
                    GLib.idle_add(self.group_overrides_cookie.add, _entry)

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
                    self.cookie_page.set_badge_number(len(file_content))

                    # Clean up fields
                    self.group_overrides_cookie.set_description("")
                    self.entry_cookie_key.set_text("")
                    self.entry_cookie_value.set_text("")
            case "parameters":
                parameter_key = self.entry_parameter_key.get_text()
                parameter_value = self.entry_parameter_value.get_text()

                if parameter_key != "" and parameter_value != "":
                    json_parameter = json.dumps(
                        {parameter_key: parameter_value}, indent=2
                    )
                    _entry = PupulatorEntry(
                        window=self,
                        override=[parameter_key, parameter_value],
                        content=PARAMETERS,
                    )
                    GLib.idle_add(self.group_overrides_parameter.add, _entry)

                    # Save paramters
                    if not os.path.exists(PARAMETERS):
                        os.makedirs(os.path.dirname(PARAMETERS), exist_ok=True)
                        with open(PARAMETERS, "w") as file:
                            file_content = file.write(json_parameter)
                    else:
                        with open(PARAMETERS, "r+") as file:
                            file_content = json.load(file)
                            file_content.update(
                                {parameter_key: parameter_value})
                            file.seek(0)
                            json.dump(file_content, file, indent=2)

                    self.parameters = file_content

                    # Clean up fields
                    self.group_overrides_parameter.set_description("")
                    self.entry_parameter_key.set_text("")
                    self.entry_parameter_value.set_text("")

    def __populate_overrides_list(self):
        """
        This function populate the list of cookies
        """
        print(dir(self.cookie_page))
        # Populate cookies
        if os.path.exists(COOKIES):
            with open(COOKIES, "r") as file:
                overrides = json.load(file)
                overrides = dict(reversed(list(overrides.items())))
                self.cookie_page.set_badge_number(len(overrides))
                self.cookies = overrides
                if not bool(overrides):
                    self.group_overrides_cookie.set_description(
                        ("No cookie added."))
                else:
                    self.cookies = overrides
                    self.group_overrides_cookie.set_description("")
                    for override in overrides:
                        _entry = PupulatorEntry(
                            window=self,
                            override=[override, overrides[override]],
                            content=COOKIES,
                        )
                        GLib.idle_add(self.group_overrides_cookie.add, _entry)
        # Populate entries
        if os.path.exists(PARAMETERS):
            with open(PARAMETERS, "r") as file:
                overrides = json.load(file)
                overrides = dict(reversed(list(overrides.items())))
                self.parameters = overrides
                if not bool(overrides):
                    self.group_overrides_parameter.set_description(
                        ("No parameter added.")
                    )
                else:
                    self.parameters = overrides
                    self.group_overrides_parameter.set_description("")
                    for override in overrides:
                        _entry = PupulatorEntry(
                            window=self,
                            override=[override, overrides[override]],
                            content=PARAMETERS,
                        )
                        GLib.idle_add(
                            self.group_overrides_parameter.add, _entry)
