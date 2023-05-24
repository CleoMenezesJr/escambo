# Copyright 2023 Rafael Mardojai CM and Cleo Menezes Jr.
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime as dt

from gi.repository import Adw, GObject, Gtk


@Gtk.Template(resource_path="/io/github/cleomenezesjr/Escambo/gtk/date-row.ui")
class DateRow(Adw.ActionRow):
    __gtype_name__ = "DateRow"
    __gsignals__ = {"changed": (GObject.SIGNAL_RUN_FIRST, None, ())}

    # Child widgets
    label = Gtk.Template.Child()
    popover = Gtk.Template.Child()
    calendar = Gtk.Template.Child()
    hours = Gtk.Template.Child()
    minutes = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initial state
        self._on_data_changed()

    @property
    def datetime(self):
        # Get Gtk.Calendar data
        day = self.calendar.get_date().get_day_of_month()
        month = self.calendar.get_date().get_month()
        year = self.calendar.get_date().get_year()

        # Get spins numbers
        hour = self.hours.get_value_as_int()
        minute = self.minutes.get_value_as_int()

        return dt(year, month, day, hour, minute)

    @Gtk.Template.Callback()
    def _on_activated(self, _row):
        self.popover.popup()

    @Gtk.Template.Callback()
    def _on_data_changed(self, *args):
        # Update label
        self.label.props.label = self.datetime.strftime("%Y-%m-%d %H:%M")
        # Emit signal
        self.emit("changed")

    @Gtk.Template.Callback()
    def _add_leading_zero(self, spin_button):
        spin_button.props.text = format(int(spin_button.props.value), "02")
        return True

