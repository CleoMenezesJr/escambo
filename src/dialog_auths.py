from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/io/github/cleomenezesjr/GetOverHere/gtk/dialog-auth.ui"
)
class AuthDialog(Adw.Window):
    __gtype_name__ = "AuthDialog"

    # Region Widgets
    btn_add = Gtk.Template.Child()
    api_key_prefs = Gtk.Template.Child()
    entry_auth_key = Gtk.Template.Child()
    entry_auth_value = Gtk.Template.Child()
    add_to = Gtk.Template.Child()
    auth_type = Gtk.Template.Child()
    token_prefs = Gtk.Template.Child()
    token = Gtk.Template.Child()

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
    def on_auth_type_changed(self, arg, kwargs):
        # TODO use this method on Method type
        type = self.auth_type.props.selected_item.get_string()
        self.token_prefs.props.visible = type == "Bearer Token"
        self.api_key_prefs.props.visible = type == "Api Key"

    @Gtk.Template.Callback()
    def on_save(self, *args) -> None:
        pill_str = self.auth_type.props.selected_item.get_string()
        add_to = self.add_to.props.selected_item.get_string()
        if "Api Key" in pill_str:
            title = self.entry_auth_key.get_text()
            subtitle = self.entry_auth_value.get_text()
        else:
            title = self.token.get_text()
            subtitle = None
        id = self.content.override[0] if self.content else None

        # Insert auth
        self.window._GetoverhereWindow__save_override(
            self, "auths", title, subtitle, id, pill_str, add_to
        )
        self.close()
        if self.content:
            self.content.set_title(title)
            self.content.set_subtitle(subtitle)

    def __populate_edit_dialog(self) -> None:
        select_options = {"Api Key": 0, "Bearer Token": 1}
        auth = self.window.auths[self.content.override[0]]

        self.entry_auth_key.set_text(auth[0])
        self.entry_auth_value.set_text(auth[1] or "")
        self.auth_type.set_selected(select_options[auth[2]])
        self.auth_type.props.sensitive = False

    @Gtk.Template.Callback()
    def on_entry_changed(self, *args) -> None:
        # Enable/Disable add button
        self.btn_add.props.sensitive = (
            self.entry_auth_value.get_text()
            and self.entry_auth_value.get_text()
            or self.token.get_text()
        )
