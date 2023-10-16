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

import html
import json
import os
import threading
from datetime import datetime as dt
from typing import Callable
from urllib.parse import urlparse

from escambo.common_scripts import has_parameter, is_valid_url
from escambo.date_row import DateRow
from escambo.dialog_body import BodyDialog
from escambo.dialog_cookies import CookieDialog
from escambo.dialog_headers import HeaderDialog
from escambo.populator_entry import PopulatorEntry
from escambo.restapi import ResolveRequests
from escambo.sourceview import SourceView
from gi.repository import Adw, Gio, GLib, Gtk
from requests import Session, exceptions
from .curl_parser import CurlParser

# constants
COOKIES = os.path.join(GLib.get_user_config_dir(), "escambo", "cookies.json")
BODY = os.path.join(GLib.get_user_config_dir(), "escambo", "body.json")
PARAM = os.path.join(GLib.get_user_config_dir(), "escambo", "parameters.json")
HEADERS = os.path.join(GLib.get_user_config_dir(), "escambo", "headers.json")
AUTHS = os.path.join(GLib.get_user_config_dir(), "escambo", "auths.json")


@Gtk.Template(resource_path="/io/github/cleomenezesjr/Escambo/gtk/window.ui")
class EscamboWindow(Adw.ApplicationWindow):
    __gtype_name__ = "EscamboWindow"

    # Template objects
    toast_overlay = Gtk.Template.Child()
    leaflet = Gtk.Template.Child()

    entry_method = Gtk.Template.Child()
    entry_url = Gtk.Template.Child()

    response_stack = Gtk.Template.Child()
    response_page = Gtk.Template.Child()
    response_page_header = Gtk.Template.Child()
    raw_page_body = Gtk.Template.Child()
    form_data_page_body = Gtk.Template.Child()

    response_source_view: SourceView = Gtk.Template.Child()
    raw_source_view_body: SourceView = Gtk.Template.Child()

    home = Gtk.Template.Child()
    form_data_toggle_button_body = Gtk.Template.Child()
    raw_toggle_button_body = Gtk.Template.Child()

    btn_send_request = Gtk.Template.Child()

    expander_row_body = Gtk.Template.Child()
    create_new_body = Gtk.Template.Child()
    group_overrides_body = Gtk.Template.Child()
    counter_label_form_data_body = Gtk.Template.Child()

    entry_param_key = Gtk.Template.Child()
    entry_param_value = Gtk.Template.Child()
    btn_add_parameter = Gtk.Template.Child()
    expander_row_parameters = Gtk.Template.Child()
    form_data_page_parameters = Gtk.Template.Child()
    group_overrides_param = Gtk.Template.Child()

    switch_cookies = Gtk.Template.Child()
    cookies_page = Gtk.Template.Child()
    create_new_cookie = Gtk.Template.Child()
    group_overrides_cookies = Gtk.Template.Child()

    switch_headers = Gtk.Template.Child()
    headers_page = Gtk.Template.Child()
    create_new_header = Gtk.Template.Child()
    group_overrides_headers = Gtk.Template.Child()

    switch_auths = Gtk.Template.Child()
    auths_page = Gtk.Template.Child()
    auth_type = Gtk.Template.Child()
    api_key_auth_key = Gtk.Template.Child()
    api_key_auth_value = Gtk.Template.Child()
    api_key_auth_add_to = Gtk.Template.Child()
    api_key_prefs = Gtk.Template.Child()
    bearer_token_prefs = Gtk.Template.Child()
    bearer_token = Gtk.Template.Child()

    spinner = Gtk.Template.Child()

    __headers_widgets = []
    __cookies_widgets = []
    __params_widgets = []

    def __init__(self, **kwargs: dict) -> None:
        super().__init__(**kwargs)

        self.kwargs = kwargs
        # Ensure close session
        with Session() as session:
            self.session = session

        # Connect signals
        self.btn_send_request.connect("clicked", self.__on_send)
        # TODO: connect show_*_dialog signal from template
        self.create_new_cookie.connect(
            "activated", self._show_cookie_dialog, _("New Cookie")
        )
        self.create_new_header.connect(
            "activated", self._show_header_dialog, _("New Header")
        )
        self.create_new_body.connect(
            "activated", self._show_body_dialog, _("New Body")
        )
        self.api_key_auth_key.connect(
            "apply", self.on_auth_entry_active, "api_key_auth_key"
        )
        self.api_key_auth_value.connect(
            "apply", self.on_auth_entry_active, "api_key_auth_value"
        )
        self.bearer_token.connect(
            "apply", self.on_auth_entry_active, "bearer_token"
        )
        self.btn_add_parameter.connect(
            "clicked", 
            lambda button: self.__save_override(
                button, 
                "param", 
                self.entry_param_key.get_text(), 
                self.entry_param_value.get_text(),
                None
            )
        )

        # General
        self.cookies = self.headers = self.auths = self.body = self.param = {}

        self.settings = Gio.Settings.new("io.github.cleomenezesjr.Escambo")
        self.create_files_if_not_exists()
        self.update_states()

        self.raw_buffer = self.raw_source_view_body.get_buffer()
        self.response_buffer = self.response_source_view.get_buffer()
        self.response_source_view.props.editable = False

    def __on_send(self, *_args: tuple) -> None:
        """
        This function checks if the submitted URL is validself.

        If validated, it proceeds to generate the request,
        otherwise it returns a Toast informing that the URL
        is using bad/illegal format or that it is missing.
        """
        url = self.entry_url.get_text()
        method = self.entry_method.get_selected()

        if not url:
            self.toast_overlay.add_toast(Adw.Toast.new(_("Enter a URL")))
        else:
            if not is_valid_url(url):
                self.toast_overlay.add_toast(
                    Adw.Toast.new(
                        _("URL using bad/illegal format or missing URL")
                    )
                )
            else:
                body = self.__which_body_type(self.is_raw)
                headers = {
                    value[0]: value[1] for key, value in self.headers.items()
                }
                which_method_thread = threading.Thread(
                    target=self.__which_method,
                    args=(method, url, headers, body),
                )
                which_method_thread.daemon = True
                which_method_thread.start()

                self.spinner.props.spinning = True
                self.leaflet.set_visible_child(self.response_page)
                self.response_stack.props.visible_child_name = "loading"

    def __which_body_type(self, body_type: bool) -> dict | None:
        if not body_type:
            body = {value[0]: value[1] for key, value in self.body.items()}
        else:
            start, end = self.raw_buffer.get_bounds()
            raw_code = self.raw_buffer.get_text(start, end, True)
            if not len(raw_code) == 0:
                try:
                    body = json.loads(raw_code)
                except ValueError:
                    return self.toast_overlay.add_toast(
                        Adw.Toast.new(_("Body must be in JSON format"))
                    )
            else:
                body = None

        return body

    def __which_method(
        self,
        method: int,
        url: str,
        headers: dict | None,
        body: dict | None,
    ) -> Callable | None:
        try:
            method_list = {
                0: "get",
                1: "post",
                2: "put",
                3: "patch",
                4: "delete",
            }
            resolve_requests = ResolveRequests(
                url,
                self.session,
                cookies=self.switch_cookies.get_active() and self.cookies,
                headers=self.settings.get_boolean("headers") and headers,
                body=self.settings.get_boolean("body") and body,
                parameters=self.settings.get_boolean("parameters")
                and self.param,
                authorization=[self.auth_type, self.auths],
            )
            get_resolve_requests_attr = getattr(
                resolve_requests, f"resolve_{method_list[method]}"
            )
            response, status_code, code_type = get_resolve_requests_attr()
        except exceptions.ConnectionError:
            self.leaflet.set_visible_child(self.home)
            return self.toast_overlay.add_toast(
                Adw.Toast.new(_("Error: Couldn't resolve host name "))
            )

        # Dynamically change syntax highlight
        self._lm = SourceView()._lm
        language = self._lm.get_language(code_type)
        GLib.idle_add(self.response_buffer.set_language, language)

        # Setup response
        GLib.idle_add(self.response_buffer.set_text, response, -1)
        GLib.idle_add(self.response_page_header.set_subtitle, str(status_code))
        self.response_stack.props.visible_child_name = "response"

        # Clenup session
        self.session.cookies.clear()
        self.session.headers.clear()
        # TODO cleanup auth

    def __set_response_visibility(self, args, kwargs):
        self.leaflet.set_visible_child(self.response_page)
        self.response_stack.props.visible_child_name = "response"

    @Gtk.Template.Callback()
    def on_edit_body_btn(self, widget) -> None:
        if self.is_raw:
            self.leaflet.set_visible_child(self.raw_page_body)
        else:
            self.leaflet.set_visible_child(self.form_data_page_body)

    @Gtk.Template.Callback()
    def on_edit_param_btn(self, widget) -> None:
        self.leaflet.set_visible_child(self.form_data_page_parameters)

    @Gtk.Template.Callback()
    def go_home(self, widget) -> None:
        self.leaflet.set_visible_child(self.home)

    def update_subtitle_parameters(self, status: bool) -> None:
        if status == False: subtitle = ""
        else:
            url_entry = self.entry_url.get_text()
            parameters = [f"{i}={self.param[i]}" for i in self.param]
            parsed_url = urlparse(url_entry)
            url_query_params = parsed_url.query.split("&")
            if parsed_url.query: parameters += url_query_params
            param_position = url_entry.find("?")
            url = (url_entry[:param_position] if has_parameter(url_entry) else url_entry)
            subtitle = (
                f"{'https://' if not url_entry else url}"
                + f"?{html.escape('&').join(parameters)}"
            )

        GLib.idle_add(self.expander_row_parameters.set_subtitle, subtitle)

    def _show_cookie_dialog(self, widget, title, content=None):
        new_window = CookieDialog(
            parent_window=self, title=title, content=content
        )
        new_window.present()

    def _show_header_dialog(self, widget, title, content=None):
        new_window = HeaderDialog(
            parent_window=self, title=title, content=content
        )
        new_window.present()

    def _show_auth_dialog(self, widget, title, content=None):
        new_window = AuthDialog(
            parent_window=self, title=title, content=content
        )
        new_window.present()

    def _show_body_dialog(self, widget, title, content=None):
        new_window = BodyDialog(
            parent_window=self, title=title, content=content
        )
        new_window.present()

    def create_files_if_not_exists(self) -> None:
        files = [COOKIES, BODY, PARAM, HEADERS, AUTHS]
        auths = {"Api Key": ["", "", "Header"], "Bearer Token": [""]}
        for file in files:
            if not os.path.exists(file):
                os.makedirs(os.path.dirname(file), exist_ok=True)
                with open(file, "w") as json_file:
                    json_file.write(
                        json.dumps(auths if "auths" in file else {})
                    )

    @Gtk.Template.Callback()
    def on_auth_entry_active(self, widget, args) -> None:
        auth_type = self.auth_type.props.selected_item.get_string()
        try:
            entry_content = getattr(self, args).get_text()
        except TypeError:
            if auth_type == "Api Key":
                entry_content = widget.props.selected_item.get_string()
                args = "api_key_auth_add_to"

        entries_position = {
            "Api Key": {
                "api_key_auth_key": 0,
                "api_key_auth_value": 1,
                "api_key_auth_add_to": 2,
            },
            "Bearer Token": {"bearer_token": 0},
        }

        # Insert Auth
        with open(AUTHS, "r+") as file:
            file_content = json.load(file)
            file_content[auth_type][
                entries_position[auth_type][args]
            ] = entry_content
            file.truncate(0)
            file.seek(0)
            json.dump(file_content, file, indent=2)

        self.auths[auth_type][
            entries_position[auth_type][args]
        ] = entry_content

    def __save_override(self, *_args: tuple) -> None:
        key: str = _args[2].strip()
        value: str = _args[3].strip()
        id: str = _args[4] or dt.today().isoformat()
        match _args[1]:
            case "cookies":
                _content = self.__add_item_to_file(COOKIES, id, [key, value])
                if not any([i == id for i in self.cookies.keys()]):
                    _entry = self.__create_populator_entry(COOKIES, id, key, value, remove=lambda widget: self.__cookies_widgets.remove(widget))
                    self.__cookies_widgets.append(_entry)
                    GLib.idle_add(self.group_overrides_cookies.add, _entry)
                    self.toast_overlay.add_toast(Adw.Toast.new(_("Cookie created")))
                else:
                    self.toast_overlay.add_toast(Adw.Toast.new(_("Cookie edited")))
                self.cookies = _content
                self.cookies_page.set_badge_number(len(_content))
                self.group_overrides_cookies.set_description("")
            case "headers":
                _content = self.__add_item_to_file(HEADERS, id, [key, value])
                if not any([i == id for i in self.headers.keys()]): 
                    _entry = self.__create_populator_entry(HEADERS, id, key, value, remove=lambda widget: self.__headers_widgets.remove(widget))
                    self.__headers_widgets.append(_entry)
                    GLib.idle_add(self.group_overrides_headers.add, _entry)
                    self.toast_overlay.add_toast(Adw.Toast.new(_("Header created")))
                else:
                    self.toast_overlay.add_toast(Adw.Toast.new(_("Header edited")))
                self.headers = _content
                self.headers_page.set_badge_number(len(_content))
                self.group_overrides_headers.set_description("")
            case "body":
                title: str = _args[2]
                subtitle: str = _args[3]
                id: str = _args[4]
                insertion_date = id or dt.today().isoformat()

                if any(title == each[0] for each in self.body.values()):
                    self.toast_overlay.add_toast(
                        Adw.Toast.new(_(f"Key “{title}” already exists"))
                    )
                    return

                # Insert Body
                with open(BODY, "r+") as file:
                    file_content = json.load(file)
                    # Save Body
                    file_content[insertion_date] = [title, subtitle]
                    file.truncate(0)
                    file.seek(0)
                    json.dump(file_content, file, indent=2)

                    # Populate UI
                    _entry = self.__create_populator_entry(BODY, id, key, value, None)
                    if not any(
                        [i == insertion_date for i in self.body.keys()]
                    ):
                        GLib.idle_add(self.group_overrides_body.add, _entry)
                        self.toast_overlay.add_toast(
                            Adw.Toast.new(_("Body created"))
                        )
                    else:
                        self.toast_overlay.add_toast(
                            Adw.Toast.new(_("Body edited"))
                        )

                self.body = file_content
                self.body_counter(file_content)

                # Clean up field
                self.group_overrides_body.set_description("")
            case "param":
                if key == "" and value == "": return
                _content = self.__add_item_to_file(PARAM, key, value)
                if not any([i == key for i in self.param.keys()]):
                    _entry = self.__create_populator_entry(PARAM, key, key, value, remove=lambda w: self.__params_widgets.remove(w))
                    self.__params_widgets.append(_entry)
                    GLib.idle_add(self.group_overrides_param.add, _entry)
                else:
                    return self.toast_overlay.add_toast(Adw.Toast.new(_("Param edited")))
                self.param = _content
                self.update_subtitle_parameters(True)
                self.group_overrides_param.set_description("")
                self.entry_param_key.set_text("")
                self.entry_param_value.set_text("")

    def __add_item_to_file(self, path: str, id: str, value: str | list[str]) -> dict:
        with open(path, "r+") as file:
            file_content = json.load(file)
            # Save Header
            file_content[id] = value
            file.truncate(0)
            file.seek(0)
            json.dump(file_content, file, indent=2)
            return file_content

    def __read_file(self, path: str):
        with open(path, "r") as json_file:
            return json.load(json_file)
    
    def __create_populator_entry(self, path: str, id: str, key: str, value: str, remove) -> PopulatorEntry:
        return PopulatorEntry(
            window=self,
            override=[
                id,
                [key, value],
            ],
            content=path,
            remove=remove 
        )

    def populate_overrides_list(self, container_name: str, path: str, file, add, remove) -> None:
        if not bool(file):
            getattr(self, f"group_overrides_{container_name}").set_description((f"No {container_name} added."))
            return
        getattr(self, f"group_overrides_{container_name}").set_description("")
        for entry_id in file:
            _content = self.__read_entry_from_file(entry_id, file)
            _entry = self.__create_populator_entry(path, entry_id, _content['key'], _content['value'], remove)
            if add: add(_entry)
            GLib.idle_add(
                getattr(self, f"group_overrides_{container_name}").add, 
                _entry
            )

    def __read_entry_from_file(self, id: str, file) -> {}:
        key = id
        value = file[id]
        is_list = isinstance(file[id], list)
        list_len = len(file[id])
        if is_list and list_len > 1:
            key = file[id][0]
            value = file[id][0]
        elif is_list and list_len == 1:
            value = file[id][0]
        return { 'key': key, 'value': value }

    def body_counter(self, overrides) -> None:
        """Body counter and its visibility"""
        counter_label = self.counter_label_form_data_body
        if len(overrides) > 0:
            if counter_label.get_visible() is False:
                counter_label.set_visible(True)
            counter_label.set_label(str(len(overrides)))
        else:
            counter_label.set_visible(False)

    def set_needs_attention(self, switches=["cookies", "headers", "auths"]):
        for switch in switches:
            switch_state = getattr(self, f"switch_{switch}").get_active()
            getattr(self, f"{switch}_page").set_needs_attention(switch_state)

    def update_states(self) -> None:
        # populate lists

        # body
        self.body = self.__read_file(BODY)
        self.populate_overrides_list("body", BODY, self.body, None, None)

        # method
        method = self.settings.get_int("method-type")
        self.__populate_method(method)

        # url entry
        url_entry = self.settings.get_string("entry-url")
        self.__populate_url(url_entry)

        # body
        self.expander_row_body.set_enable_expansion(
            self.settings.get_boolean("body")
        )
        self.body_counter(self.body)
        self.is_raw = self.settings.get_boolean("body-type")
        self.form_data_toggle_button_body.props.active = not self.is_raw

        # parameters
        self.param = self.__read_file(PARAM)
        self.populate_overrides_list(
            "param", 
            PARAM, 
            self.param, 
            lambda w: self.__params_widgets.append(w), 
            lambda w: self.__params_widgets.remove(w)
        )
        use_params = self.settings.get_boolean("parameters")
        has_params = len(self.param) > 0
        self.__param_status_changed(use_params and has_params)
        self.__populate_params_status(use_params and has_params)

        # cookies
        self.cookies = self.__read_file(COOKIES)
        self.populate_overrides_list(
            "cookies", 
            COOKIES, 
            self.cookies, 
            lambda w: self.__cookies_widgets.append(w), 
            lambda w: self.__cookies_widgets.remove(w)
        )
        use_cookies = self.settings.get_boolean("cookies")
        has_cookies = len(self.cookies) > 0
        self.__cookies_status_changed(use_cookies and has_cookies)
        self.__populate_cookies_status(use_cookies and has_cookies)

        # headers
        self.headers = self.__read_file(HEADERS)
        self.populate_overrides_list(
            "headers", 
            HEADERS, 
            self.headers, 
            lambda w: self.__headers_widgets.append(w), 
            lambda w: self.__headers_widgets.remove(w)
        )
        use_headers: bool = self.settings.get_boolean("headers")
        has_headers: bool = len(self.headers) > 0
        self.__headers_status_changed(use_headers and has_headers)
        self.__populate_headers_status(use_headers and has_headers)

        # auths
        auth_type = self.settings.get_int("auth-type")
        self.__populate_auth(False, auth_type)

        self.set_needs_attention()

    @Gtk.Template.Callback()
    def on_entry_method_changed(self, widget, args) -> None:
        self.__method_changed(widget.get_selected())

    def __method_changed(self, value: int) -> None:
        self.settings.set_int("method-type", value)

    def __populate_method(self, value: int) -> None:
        self.entry_method.set_selected(value)

    @Gtk.Template.Callback()
    def on_entry_url_changed(self, widget) -> None:
        self.__url_changed(widget.get_text())

    def __url_changed(self, value: str) -> None:
        self.settings.set_string("entry-url", value)
        self.update_subtitle_parameters(self.settings.get_boolean("parameters"))
        
    def __populate_url(self, value: str) -> None:
        self.entry_url.set_text(value)

    @Gtk.Template.Callback()
    def on_param_switch_changed(self, widget: Adw.ExpanderRow, args) -> None:
        self.__param_status_changed(widget.get_enable_expansion())
        self.update_subtitle_parameters(self.settings.get_boolean("parameters"))

    def __param_status_changed(self, status: bool) -> None:
        self.settings.set_boolean("parameters", status)

    def __populate_params_status(self, status: bool) -> None:
        self.expander_row_parameters.set_expanded(status)
        self.expander_row_parameters.set_enable_expansion(status)
        self.update_subtitle_parameters(status)

    @Gtk.Template.Callback()
    def on_body_switch_changed(self, widget, args) -> None:
        self.settings.set_boolean("body", widget.get_enable_expansion())
        self.body_counter(self.body)

    @Gtk.Template.Callback()
    def on_body_type_changed(self, widget) -> None:
        self.is_raw = widget.props.active
        self.settings.set_boolean("body-type", self.is_raw)

    @Gtk.Template.Callback()
    def on_cookies_switch_state_change(self, widget, state) -> None:
        self.__cookies_status_changed(state)
        self.cookies_page.set_badge_number(len(self.cookies))
        self.set_needs_attention(switches=["cookies"])

    def __cookies_status_changed(self, status: bool) -> None:
        self.settings.set_boolean("cookies", status)

    def __populate_cookies_status(self, status: bool) -> None:
        self.switch_cookies.set_active(status)
        self.cookies_page.set_badge_number(len(self.cookies))

    @Gtk.Template.Callback()
    def on_headers_switch_state_change(self, widget, state) -> None:
        self.__headers_status_changed(state)
        self.headers_page.set_badge_number(len(self.headers))
        self.set_needs_attention(switches=["headers"])

    def __headers_status_changed(self, status: bool) -> None:
        self.settings.set_boolean("headers", status)

    def __populate_headers_status(self, status: bool) -> None:
        self.switch_headers.set_active(status)
        self.headers_page.set_badge_number(len(self.headers))

    @Gtk.Template.Callback()
    def on_auths_switch_state_change(self, widget, state) -> None:
        self.__auths_state_changed(state)
        self.set_needs_attention(switches=["auths"])

    def __auths_state_changed(self, state: bool) -> None:
        self.settings.set_boolean("auths", state)

    @Gtk.Template.Callback()
    def on_auth_type_changed(self, widget, args):
        selected = widget.get_selected()
        self.__auths_type_changed(selected)

    def __auths_type_changed(self, value: int) -> None:
        self.settings.set_int("auth-type", value)
        self.bearer_token_prefs.props.visible = value == 1
        self.api_key_prefs.props.visible = value == 0

    def __populate_from_curl(self, curl: CurlParser) -> None:

        # URL
        self.__url_changed(curl.url)
        self.__populate_url(curl.url)

        # Method
        method_list = {
            "get": 0,
            "post": 1,
            "put": 2,
            "patch": 3,
            "delete": 4,
        }
        method_id = method_list[curl.method.lower()]
        self.__method_changed(method_id)
        self.__populate_method(method_id)

        #Authorization
        token = curl.authorization
        self.__auths_state_changed(token != None)
        self.__auths_type_changed(1)
        self.__populate_auth(token != None, 1)
        if token != None: self.__populate_token(token)
        else: self.__populate_token("")

        #Headers
        headers = curl.headers
        has_headers = len(headers) > 0
        self.__clear_headers()
        self.__headers_status_changed(has_headers)
        self.__populate_headers_status(has_headers)
        if (has_headers):
            for key in headers:
                self.__save_override(None, "headers", key, headers[key], None)

        #Cookies
        cookies = curl.cookies
        has_cookies = len(cookies) > 0
        self.__clear_cookies()
        self.__cookies_status_changed(has_cookies)
        self.__populate_cookies_status(has_cookies)
        if (has_cookies):
            for key in cookies:
                self.__save_override(None, "cookies", key, cookies[key], None)

        #Params
        params = curl.params
        has_params = len(params) > 0
        self.__clear_params()
        self.__param_status_changed(has_params)
        self.__populate_params_status(has_params)
        if has_params:
            for key in params:
                self.__save_override(None, "param", key, params[key], None)


        self.set_needs_attention()

    def __populate_auth(self, use_auth: bool, auth_type: int) -> None:
        self.switch_auths.set_active(use_auth)
        self.auth_type.set_selected(auth_type)

    def __populate_token(self, token: str) -> None:
        self.bearer_token.set_text(token)

    def __clear_headers(self) -> None:
        self.headers = {}
        self.__clear_file(HEADERS)
        for widget in self.__headers_widgets:
            self.group_overrides_headers.remove(widget)
        self.__headers_widgets.clear()

    def __clear_file(self, file: str) -> None:
        with open(file, "w") as json_file:
            json_file.write(
                json.dumps({})
            )

    def __clear_cookies(self) -> None:
        self.cookies = {}
        self.__clear_file(COOKIES)
        for widget in self.__cookies_widgets:
            self.group_overrides_cookies.remove(widget)
        self.__cookies_widgets.clear()

    def __clear_params(self) -> None:
        self.param = {}
        self.__clear_file(PARAM)
        for widget in self.__params_widgets:
            self.group_overrides_param.remove(widget)
        self.__params_widgets.clear()
