from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/io/github/cleomenezesjr/Escambo/gtk/dialog-body.ui"
)
class BodyDialog(Adw.Window):
    __gtype_name__ = "BodyDialog"

    # Region Widgets
    btn_add = Gtk.Template.Child()
    entry_body_key = Gtk.Template.Child()
    entry_body_value = Gtk.Template.Child()

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
        title = self.entry_body_key.get_text()
        subtitle = self.entry_body_value.get_text()
        id = self.content.override[0] if self.content else None

        # Insert Body
        self.window._EscamboWindow__save_override(
            self, "body", title, subtitle, id
        )
        self.close()
        if self.content:
            self.content.set_title(title)
            self.content.set_subtitle(subtitle)

    def __populate_edit_dialog(self) -> None:
        body = self.window.body[self.content.override[0]]

        self.entry_body_key.set_text(body[0])
        self.entry_body_value.set_text(body[1])

    @Gtk.Template.Callback()
    def on_entry_changed(self, *args) -> None:
        # Enable/Disable add button
        self.btn_add.props.sensitive = (
            self.entry_body_key.get_text() and self.entry_body_value.get_text()
        )

