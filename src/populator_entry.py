import json

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path="/io/github/cleomenezesjr/GetOverHere/populator-entry.ui")
class PupulatorEntry(Adw.ActionRow):
    __gtype_name__ = "PupulatorEntry"

    # region Widgets
    btn_remove = Gtk.Template.Child()

    # endregion

    def __init__(self, window, override, content, **kwargs):
        super().__init__(**kwargs)

        # common variables and references
        self.window = window
        self.override = override
        self.content = content

        """
        Set the DLL name as ActionRow title and set the
        combo_type to the type of override
        """
        self.set_title(self.override[0])
        self.set_subtitle(self.override[1])

        # connect signals
        self.btn_remove.connect("clicked", self.__remove_override)

    def __remove_override(self, *_args):
        """
        Remove Cookie and destroy the widget
        """
        with open(self.content, "r+") as file:
            file_content = json.load(file)
            file_content.pop(self.override[0])
            file.seek(0)
            json.dump(file_content, file, indent=2)
            file.truncate()

        if not bool(file_content):
            if "cookies" in self.content:
                self.window.get_template_child(
                    self.window, "group_overrides_cookie"
                ).set_description("No cookie added.")

            elif "parameters" in self.content:
                self.window.get_template_child(
                    self.window, "group_overrides_parameter"
                ).set_description("No parameter added.")

        self.window.cookie_page.set_badge_number(len(file_content))
        self.window.parameter_counter(file_content)

        self.get_parent().remove(self)
