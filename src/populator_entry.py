import json

from escambo.dialog_body import BodyDialog
from escambo.dialog_cookies import CookieDialog
from escambo.dialog_headers import HeaderDialog
from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/io/github/cleomenezesjr/Escambo/gtk/populator-entry.ui"
)
class PopulatorEntry(Adw.ActionRow):
    __gtype_name__ = "PopulatorEntry"

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
        if any(i in self.content for i in ["cookies", "headers", "body"]):
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

        # update status
        self.window.update_subtitle_parameters()
        # connect signals
        self.btn_remove.connect("clicked", self.__remove_override)

    def __remove_override(self, *_args) -> None:
        """
        Remove element and destroy the widget
        """

        def resolve_dialog_response(widget, response):
            if response == "ok":
                # if not bool(file_content):
                files = {
                    "cookie": "cookies",
                    "header": "headers",
                    "body": "body",
                    "parameter": "param",
                }
                for file in files:
                    if files[file] in self.content:
                        file_content = getattr(self.window, files[file])
                        del file_content[self.override[0]]
                        with open(self.content, "w") as json_content:
                            json.dump(file_content, json_content, indent=2)

                        self.window.cookies = (
                            file_content
                            if "cookie" in file
                            else self.window.cookies
                        )
                        self.window.body = (
                            file_content
                            if "body" in file
                            else self.window.body
                        )
                        self.window.param = (
                            file_content
                            if "parameter" in file
                            else self.window.param
                        )
                        self.window.headers = (
                            file_content
                            if "header" in file
                            else self.window.headers
                        )
                        if len(file_content) == 0:
                            getattr(
                                self.window, f"group_overrides_{files[file]}"
                            ).set_description((f"No {file} added."))

                # update status
                self.window.update_subtitle_parameters()

                self.window.cookies_page.set_badge_number(
                    len(self.window.cookies)
                )
                self.window.headers_page.set_badge_number(
                    len(self.window.headers)
                )
                self.window.body_counter(self.window.body)
                # TODO
                # Remove query parameter on subtitle

                self.get_parent().remove(self)

        subtitle = f"\n{self.get_subtitle()}" if self.get_subtitle() else ""
        dialog = Adw.MessageDialog.new(
            self.window,
            _("Are you sure you want to delete it?"),
            (f"{self.get_title()}{subtitle}"),
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("ok", _("Delete"))
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
                title=_("Edit Cookie"),
                content=self,
            )
            new_window.present()
        elif "headers" in self.content:
            new_window = HeaderDialog(
                parent_window=self.window,
                title=_("Edit Header"),
                content=self,
            )
            new_window.present()
        elif "body" in self.content:
            new_window = BodyDialog(
                parent_window=self.window,
                title=_("Edit Body"),
                content=self,
            )
            new_window.present()
