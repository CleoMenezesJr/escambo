# Copyright 2022 Cleo Menezes Jr.
from gi.repository import Adw, Gtk, GtkSource


class SourceView(GtkSource.View):
    __gtype_name__ = "SourceView"

    def __init__(self) -> None:
        super().__init__()

        self.props.show_line_numbers = True
        self.props.monospace = True
        self.props.wrap_mode = Gtk.WrapMode.WORD_CHAR
        self.props.hexpand = True

        self._lm = GtkSource.LanguageManager()
        self.lang = "json"
        language = self._lm.get_language(self.lang)

        self.text_buffer = self.get_buffer()
        self.text_buffer.set_highlight_matching_brackets(True)
        self.text_buffer.set_language(language)

        ssm = GtkSource.StyleSchemeManager()
        self._adwaita = ssm.get_scheme("Adwaita")
        self._adwaita_dark = ssm.get_scheme("Adwaita-dark")

        style_manager = Adw.StyleManager.get_default()
        style_manager.connect("notify::dark", self._on_dark_style)
        self._on_dark_style(style_manager)

    def _on_dark_style(self, style_manager: classmethod, *args) -> None:
        if style_manager.props.dark:
            self.text_buffer.set_style_scheme(self._adwaita_dark)
        else:
            self.text_buffer.set_style_scheme(self._adwaita)

