import json

from getoverhere.dialog_cookies import CookieDialog
from getoverhere.dialog_headers import HeaderDialog
from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/io/github/cleomenezesjr/GetOverHere/gtk/populator-entry.ui"
)
class PupulatorEntry(Adw.ActionRow):
    __gtype_name__ = "PupulatorEntry"

    # region Widgets
    btn_remove = Gtk.Template.Child()

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
        if "cookies" in self.content or "headers" in self.content:
            self.set_title(self.override[1][0] or "—")
            self.set_subtitle(self.override[1][1] or "—")
        elif "auths" in self.content:
            self.window.api_key_auth_key.set_text(self.override["Api Key"][0])
            self.window.api_key_auth_value.set_text(
                self.override["Api Key"][1]
            )
            select_options = {"Header": 0, "Query Parameters": 1}
            self.window.api_key_auth_add_to.set_selected(
                select_options[self.override["Api Key"][2]]
            )

            self.window.bearer_token.set_text(self.override["Bearer Token"][0])
        else:
            self.set_title(self.override[0])
            self.set_subtitle(self.override[1])

        # connect signals
        self.btn_remove.connect("clicked", self.__remove_override)

    def __remove_override(self, *_args) -> None:
        """
        Remove element and destroy the widget
        """

        def resolve_dialog_response(widget, response):
            if response == "ok":
                # if not bool(file_content):
                if "cookies" in self.content:
                    file_content = self.window.cookies
                    del file_content[self.override[0]]
                    with open(self.content, "w") as file:
                        json.dump(file_content, file, indent=2)

                    if len(file_content) == 0:
                        self.window.get_template_child(
                            self.window, "group_overrides_cookies"
                        ).set_description("No cookie added.")

                elif "headers" in self.content:
                    file_content = self.window.headers
                    del file_content[self.override[0]]
                    with open(self.content, "w") as file:
                        json.dump(file_content, file, indent=2)

                    if len(file_content) == 0:
                        self.window.get_template_child(
                            self.window, "group_overrides_headers"
                        ).set_description("No header added.")
                elif "body" in self.content:
                    self.window.get_template_child(
                        self.window, "group_overrides_body"
                    ).set_description("No body added.")
                elif "param" in self.content:
                    self.window.get_template_child(
                        self.window, "group_overrides_params"
                    ).set_description("No parameter added.")
                    self.window.enable_expander_row_parameters.set_subtitle(
                        "https://?"
                    )
                    self.window.param = {}

                # TODO
                # Remove query parameter on subtitle
                # TODO set badge per file_content
                self.window.cookie_page.set_badge_number(len(file_content))
                self.window.headers_page.set_badge_number(len(file_content))
                self.window.body_counter(file_content)

                # Update subtitle

                self.get_parent().remove(self)

        subtitle = f"\n{self.get_subtitle()}" if self.get_subtitle() else ""
        dialog = Adw.MessageDialog.new(
            self.window,
            "Are you sure you want to delete it?",
            (f"{self.get_title()}{subtitle}"),
        )
        dialog.add_response("cancel", ("Cancel"))
        dialog.add_response("ok", ("Delete"))
        dialog.set_response_appearance(
            "ok", Adw.ResponseAppearance.DESTRUCTIVE
        )
        dialog.connect("response", resolve_dialog_response)
        dialog.present()

    @Gtk.Template.Callback()
    def on_edit(self, arg) -> None:
        if "cookies" in self.content:
            new_window = CookieDialog(
                parent_window=self.window,
                title="Edit Cookie",
                content=self,
            )
            new_window.present()
        elif "headers" in self.content:
            new_window = HeaderDialog(
                parent_window=self.window,
                title="Edit Header",
                content=self,
            )
            new_window.present()
