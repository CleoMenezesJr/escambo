from datetime import datetime as dt

from getoverhere.commom_scripts import str_to_dict_cookie, stringfy_cookie
from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/io/github/cleomenezesjr/GetOverHere/gtk/dialog-cookies.ui"
)
class CookieDialog(Adw.Window):
    __gtype_name__ = "CookieDialog"

    # Region Widgets
    btn_add = Gtk.Template.Child()
    entry_cookie_key = Gtk.Template.Child()
    entry_cookie_value = Gtk.Template.Child()
    entry_cookie_domain = Gtk.Template.Child()
    entry_cookie_path = Gtk.Template.Child()
    entry_cookie_expires = Gtk.Template.Child()
    expander_row_expires = Gtk.Template.Child()

    def __init__(self, parent_window, title, content, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(parent_window)
        self.set_title(title)

        # Common variables and references
        self.window = parent_window
        self.content = content

        # Initial setup
        if content:
            self.__populate_edit_dialog()

    @Gtk.Template.Callback()
    def on_save(self, *args) -> None:
        # Convert date format to GMT format
        entry_cookie_expires = (
            self.entry_cookie_expires.label.get_text().replace("-", "/")
        )
        cookie_expires_gmt = dt.strptime(
            entry_cookie_expires, "%Y/%m/%d %H:%M"
        ).strftime("%a, %d %b %Y %H:%M:%S GMT")

        switch_expires_state = self.expander_row_expires.get_enable_expansion()
        title = self.entry_cookie_domain.get_text()
        subtitle = stringfy_cookie(
            self.entry_cookie_key.get_text(),
            self.entry_cookie_value.get_text(),
            cookie_expires_gmt if switch_expires_state else "",
            self.entry_cookie_domain.get_text(),
            self.entry_cookie_path.get_text(),
            self.content.override[0] if self.content else "",
        )
        id = self.content.override[0] if self.content else None

        # Insert Cookie
        self.window._GetoverhereWindow__save_override(
            self, "cookies", title, subtitle, id
        )
        self.close()
        if self.content:
            self.content.set_title(title)
            self.content.set_subtitle(subtitle)

    def __populate_edit_dialog(self) -> None:
        # get value from cookies variable
        cookie = str_to_dict_cookie(
            self.window.cookies, self.content.override[0]
        )

        self.entry_cookie_key.set_text(cookie["name"])
        self.entry_cookie_value.set_text(cookie["value"])
        if "domain" in cookie.keys():
            self.entry_cookie_domain.set_text(cookie["domain"])
        if "path" in cookie.keys():
            self.entry_cookie_path.set_text(cookie["path"])
        if "expires" in cookie.keys():
            self.expander_row_expires.set_enable_expansion(True)
            expires = dt.strptime(
                cookie["expires"], "%a, %d %b %Y %H:%M:%S %Z"
            ).strftime("%Y-%m-%d %H:%M")
            self.entry_cookie_expires.label.set_text(expires)

    @Gtk.Template.Callback()
    def on_entry_changed(self, *args) -> None:
        # Enable/Disable add button
        if (
            not self.entry_cookie_key.get_text()
            or not self.entry_cookie_value.get_text()
        ):
            self.btn_add.props.sensitive = False
        else:
            self.btn_add.props.sensitive = True
