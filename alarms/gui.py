"""Simple Tkinter-based graphical interface for managing alarms."""

from __future__ import annotations

import threading
import tkinter as tk
from datetime import datetime
from queue import Empty, Queue
from tkinter import messagebox, ttk
from typing import List, Optional

from .manager import AlarmManager
from .models import Alarm
from .scheduler import AlarmScheduler, preview_schedule


WEEKDAY_NAMES = [
    "Poniedziałek",
    "Wtorek",
    "Środa",
    "Czwartek",
    "Piątek",
    "Sobota",
    "Niedziela",
]


class AlarmApp:
    """Graphical application that wraps :class:`AlarmManager`."""

    def __init__(self, manager: Optional[AlarmManager] = None) -> None:
        self.manager = manager or AlarmManager()
        self.root = tk.Tk()
        self.root.title("Alarmy")
        self.root.geometry("640x480")

        self._scheduler: Optional[AlarmScheduler] = None
        self._scheduler_thread: Optional[threading.Thread] = None
        self._notification_queue: "Queue[str]" = Queue()

        self._build_layout()
        self.refresh_list()
        self._schedule_notification_poll()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Layout
    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # Alarm list
        tree_frame = ttk.LabelFrame(main, text="Zdefiniowane budziki")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("time", "label", "days", "enabled")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.tree.heading("time", text="Godzina")
        self.tree.heading("label", text="Etykieta")
        self.tree.heading("days", text="Harmonogram")
        self.tree.heading("enabled", text="Aktywny")
        self.tree.column("time", width=80, anchor=tk.CENTER)
        self.tree.column("label", width=200, anchor=tk.W)
        self.tree.column("days", width=200, anchor=tk.W)
        self.tree.column("enabled", width=80, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)

        # Form for new alarm
        form = ttk.LabelFrame(main, text="Dodaj nowy budzik", padding=12)
        form.pack(fill=tk.X, pady=(12, 0))

        ttk.Label(form, text="Godzina (HH:MM)").grid(row=0, column=0, sticky=tk.W)
        self.time_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.time_var, width=10).grid(row=1, column=0, sticky=tk.W)

        ttk.Label(form, text="Etykieta").grid(row=0, column=1, sticky=tk.W, padx=(12, 0))
        self.label_var = tk.StringVar(value="Nowy budzik")
        ttk.Entry(form, textvariable=self.label_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=(12, 0))

        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Aktywny", variable=self.enabled_var).grid(row=1, column=2, padx=(12, 0))

        days_frame = ttk.Frame(form)
        days_frame.grid(row=2, column=0, columnspan=3, pady=(12, 0), sticky=tk.W)
        ttk.Label(days_frame, text="Dni powtórzeń:").pack(side=tk.LEFT)

        self.day_vars: List[tk.BooleanVar] = []
        for index, name in enumerate(WEEKDAY_NAMES):
            var = tk.BooleanVar(value=False)
            check = ttk.Checkbutton(days_frame, text=name[:3], variable=var)
            check.pack(side=tk.LEFT, padx=3)
            self.day_vars.append(var)

        button_frame = ttk.Frame(form)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(12, 0), sticky=tk.W)
        ttk.Button(button_frame, text="Dodaj budzik", command=self.add_alarm).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Usuń zaznaczony", command=self.remove_selected).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="Aktywuj/Dezaktywuj", command=self.toggle_selected).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Odśwież", command=self.refresh_list).pack(side=tk.LEFT, padx=6)

        scheduler_frame = ttk.LabelFrame(main, text="Harmonogram", padding=12)
        scheduler_frame.pack(fill=tk.X, pady=(12, 0))

        ttk.Button(
            scheduler_frame,
            text="Podgląd najbliższych",
            command=self.preview_alarms,
        ).pack(side=tk.LEFT)

        ttk.Button(
            scheduler_frame,
            text="Uruchom harmonogram",
            command=self.start_scheduler,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            scheduler_frame,
            text="Zatrzymaj harmonogram",
            command=self.stop_scheduler,
        ).pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Helpers
    def _collect_selected_days(self) -> List[int]:
        return [index for index, var in enumerate(self.day_vars) if var.get()]

    def _set_tree_item(self, alarm: Alarm) -> None:
        schedule = alarm.describe_schedule()
        values = (alarm.time_str, alarm.label, schedule, "Tak" if alarm.enabled else "Nie")
        self.tree.insert("", tk.END, iid=alarm.alarm_id, values=values)

    def refresh_list(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for alarm in self.manager.list_alarms():
            self._set_tree_item(alarm)

    # ------------------------------------------------------------------
    # Button callbacks
    def add_alarm(self) -> None:
        time_value = self.time_var.get().strip()
        label = self.label_var.get().strip() or "Alarm"
        repeat_days = self._collect_selected_days()
        try:
            alarm = self.manager.add_alarm(time_value, label=label, repeat_days=repeat_days, enabled=self.enabled_var.get())
        except ValueError as exc:
            messagebox.showerror("Błąd", str(exc))
            return
        self._set_tree_item(alarm)
        messagebox.showinfo("Sukces", "Dodano nowy budzik.")

    def remove_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Brak wyboru", "Zaznacz budzik do usunięcia.")
            return
        removed_any = False
        for item in selection:
            alarm_id = item
            if self.manager.remove_alarm(alarm_id):
                self.tree.delete(item)
                removed_any = True
        if removed_any:
            messagebox.showinfo("Sukces", "Usunięto wybrane budziki.")

    def toggle_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Brak wyboru", "Zaznacz budzik do przełączenia.")
            return
        for item in selection:
            alarm_id = item
            alarm = self.manager.get_alarm(alarm_id)
            if not alarm:
                continue
            self.manager.toggle_alarm(alarm_id, not alarm.enabled)
        self.refresh_list()

    def preview_alarms(self) -> None:
        upcoming = preview_schedule(self.manager.list_alarms(), count=5)
        if not upcoming:
            messagebox.showinfo("Podgląd", "Brak aktywnych budzików.")
            return
        messagebox.showinfo("Podgląd", upcoming)

    # ------------------------------------------------------------------
    # Scheduler handling
    def start_scheduler(self) -> None:
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            messagebox.showinfo("Harmonogram", "Harmonogram już działa.")
            return

        def notifier(alarm: Alarm, trigger_time: datetime) -> None:
            formatted = f"{trigger_time:%Y-%m-%d %H:%M} — {alarm.label}"
            self._notification_queue.put(formatted)

        self._scheduler = AlarmScheduler(self.manager, notifier=notifier)
        self._scheduler_thread = threading.Thread(target=self._scheduler.run, daemon=True)
        self._scheduler_thread.start()
        messagebox.showinfo("Harmonogram", "Uruchomiono harmonogram w tle.")

    def stop_scheduler(self) -> None:
        if self._scheduler:
            self._scheduler.stop()
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=0.5)
        self._scheduler_thread = None
        self._scheduler = None
        messagebox.showinfo("Harmonogram", "Harmonogram zatrzymany.")

    def _schedule_notification_poll(self) -> None:
        try:
            while True:
                message = self._notification_queue.get_nowait()
                messagebox.showinfo("Budzik", message)
        except Empty:
            pass
        finally:
            self.root.after(500, self._schedule_notification_poll)

    # ------------------------------------------------------------------
    def _on_close(self) -> None:
        if self._scheduler:
            self._scheduler.stop()
        self.root.destroy()

    def run(self) -> None:
        """Start the Tkinter main loop."""

        self.root.mainloop()


def launch(manager: Optional[AlarmManager] = None) -> None:
    """Convenience helper to start the GUI."""

    app = AlarmApp(manager=manager)
    app.run()


if __name__ == "__main__":  # pragma: no cover - manual usage
    launch()
