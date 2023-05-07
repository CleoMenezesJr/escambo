from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/io/github/cleomenezesjr/GetOverHere/gtk/environments.ui"
)
class EnvironmentsWindow(Adw.Window):
    __gtype_name__ = "EnvironmentsWindow"

    # Region Widgets
    # btn_add = Gtk.Template.Child()
    # entry_cookie_key = Gtk.Template.Child()
    # entry_cookie_value = Gtk.Template.Child()
    # entry_cookie_domain = Gtk.Template.Child()
    # entry_cookie_path = Gtk.Template.Child()
    # entry_cookie_expires = Gtk.Template.Child()
    # expander_row_expires = Gtk.Template.Child()
    #
    def __init__(self, parent_window, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(parent_window)
        # self.set_title()

        # Common variables and references
        # self.window = parent_window
        # self.content = content

        # Initial setup
        # if content:
        #     self.__populate_edit_dialog()
