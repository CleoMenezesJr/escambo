from gi.repository import Adw, Gtk
from .curl_parser import CurlParser

@Gtk.Template(
    resource_path="/io/github/cleomenezesjr/Escambo/gtk/dialog-import.ui"
)
class ImportDialog(Adw.Window):
    __gtype_name__ = "ImportDialog"

    btn_import = Gtk.Template.Child()
    entry_curl = Gtk.Template.Child()

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(parent)
        self.set_title("Import")
        self.__window = parent

    @Gtk.Template.Callback()
    def on_import(self, *args) -> None:
        print("On import")
        value = self.entry_curl.get_text()
        parsed = CurlParser(value)
        self.__window._EscamboWindow__populate_from_curl(parsed)
        self.close()

    @Gtk.Template.Callback()
    def on_entry_changed(self, *args) -> None:
        # Enable/Disable add button
        self.btn_import.props.sensitive = (
            self.entry_curl.get_text()
        )