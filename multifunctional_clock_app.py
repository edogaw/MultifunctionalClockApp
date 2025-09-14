#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Beauty Clock App (Python + Tkinter + ttkbootstrap)
- Analog + Digital Clock
- Stopwatch (smooth + accurate)
- Timer (accurate countdown)
- Alarms with reminders
- Elegant UI with ttkbootstrap themes
"""

import time, math, datetime
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ---------- Smooth Analog Clock ----------
class SmoothAnalog(tk.Canvas):
    def __init__(self, parent, size=400, fps=60, bg=None, *args, **kwargs):
        style = ttk.Style()
        default_bg = style.lookup("TFrame", "background") or "#222222"

        self.size = size
        self.center = size // 2
        self.radius = size // 2 - 20
        self.fps = fps
        self.bg = bg if bg else default_bg

        super().__init__(parent, width=size, height=size,
                         bg=self.bg, highlightthickness=0, *args, **kwargs)

        self.hands = {}
        self._draw_clock_face()
        self._update()

    def _draw_clock_face(self):
        self.create_oval(10, 10, self.size-10, self.size-10,
                         width=4, outline="#3bc9db")

        for i in range(60):
            angle = math.radians(i * 6)
            x0 = self.center + (self.radius - 10) * math.sin(angle)
            y0 = self.center - (self.radius - 10) * math.cos(angle)
            x1 = self.center + self.radius * math.sin(angle)
            y1 = self.center - self.radius * math.cos(angle)
            width = 4 if i % 5 == 0 else 2
            color = "#15aabf" if i % 5 == 0 else "#4dabf7"
            self.create_line(x0, y0, x1, y1, width=width, fill=color)

        self.hands["hour"] = self.create_line(
            self.center, self.center, self.center, self.center - self.radius * 0.5,
            width=8, fill="#ff6b6b", capstyle=tk.ROUND
        )
        self.hands["minute"] = self.create_line(
            self.center, self.center, self.center, self.center - self.radius * 0.75,
            width=6, fill="#ffd43b", capstyle=tk.ROUND
        )
        self.hands["second"] = self.create_line(
            self.center, self.center, self.center, self.center - self.radius * 0.9,
            width=3, fill="#69db7c", capstyle=tk.ROUND
        )

    def _update(self):
        now = datetime.datetime.now()
        ms = now.microsecond / 1_000_000

        sec = now.second + ms
        minute = now.minute + sec / 60
        hour = (now.hour % 12) + minute / 60

        self._set_hand("hour", (hour/12)*360, 0.5*self.radius)
        self._set_hand("minute", (minute/60)*360, 0.75*self.radius)
        self._set_hand("second", (sec/60)*360, 0.9*self.radius)

        self.after(int(1000/self.fps), self._update)

    def _set_hand(self, name, angle_deg, length):
        angle = math.radians(angle_deg)
        x = self.center + length * math.sin(angle)
        y = self.center - length * math.cos(angle)
        self.coords(self.hands[name], self.center, self.center, x, y)

# ---------- Stopwatch Tab ----------
class StopwatchTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.running = False
        self.start_time = None
        self.elapsed = 0.0

        self.label = ttk.Label(self, text="00:00:00.00",
                               font=("Consolas", 48), bootstyle="success")
        self.label.pack(pady=20)

        btns = ttk.Frame(self)
        btns.pack(pady=10)

        ttk.Button(btns, text="Start", command=self.start,
                   bootstyle="success-outline").pack(side=LEFT, padx=5)
        ttk.Button(btns, text="Stop", command=self.stop,
                   bootstyle="danger-outline").pack(side=LEFT, padx=5)
        ttk.Button(btns, text="Reset", command=self.reset,
                   bootstyle="warning-outline").pack(side=LEFT, padx=5)

    def _update(self):
        if self.running:
            now = time.perf_counter()
            total = self.elapsed + (now - self.start_time)
            mins, secs = divmod(total, 60)
            hrs, mins = divmod(mins, 60)
            self.label.config(text=f"{int(hrs):02}:{int(mins):02}:{secs:05.2f}")
            self.after(20, self._update)

    def start(self):
        if not self.running:
            self.start_time = time.perf_counter()
            self.running = True
            self._update()

    def stop(self):
        if self.running:
            self.elapsed += time.perf_counter() - self.start_time
            self.running = False

    def reset(self):
        self.running = False
        self.start_time = None
        self.elapsed = 0.0
        self.label.config(text="00:00:00.00")

# ---------- Timer Tab ----------
class TimerTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.running = False
        self.end_time = None

        self.label = ttk.Label(self, text="00:00:00",
                               font=("Consolas", 48), bootstyle="info")
        self.label.pack(pady=20)

        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)

        self.hrs = tk.IntVar(value=0)
        self.mins = tk.IntVar(value=0)
        self.secs = tk.IntVar(value=0)

        ttk.Entry(input_frame, textvariable=self.hrs, width=3).pack(side=LEFT, padx=2)
        ttk.Label(input_frame, text="h").pack(side=LEFT)
        ttk.Entry(input_frame, textvariable=self.mins, width=3).pack(side=LEFT, padx=2)
        ttk.Label(input_frame, text="m").pack(side=LEFT)
        ttk.Entry(input_frame, textvariable=self.secs, width=3).pack(side=LEFT, padx=2)
        ttk.Label(input_frame, text="s").pack(side=LEFT)

        btns = ttk.Frame(self)
        btns.pack(pady=10)

        ttk.Button(btns, text="Start", command=self.start,
                   bootstyle="success-outline").pack(side=LEFT, padx=5)
        ttk.Button(btns, text="Stop", command=self.stop,
                   bootstyle="danger-outline").pack(side=LEFT, padx=5)
        ttk.Button(btns, text="Reset", command=self.reset,
                   bootstyle="warning-outline").pack(side=LEFT, padx=5)

    def _update(self):
        if self.running:
            remaining = self.end_time - time.perf_counter()
            if remaining <= 0:
                self.label.config(text="00:00:00")
                self.running = False
                messagebox.showinfo("Timer", "Time is up!")
                return
            mins, secs = divmod(remaining, 60)
            hrs, mins = divmod(mins, 60)
            self.label.config(text=f"{int(hrs):02}:{int(mins):02}:{int(secs):02}")
            self.after(200, self._update)

    def start(self):
        total = self.hrs.get()*3600 + self.mins.get()*60 + self.secs.get()
        if total <= 0:
            messagebox.showwarning("Invalid", "Enter a valid duration")
            return
        self.end_time = time.perf_counter() + total
        self.running = True
        self._update()

    def stop(self):
        self.running = False

    def reset(self):
        self.running = False
        self.label.config(text="00:00:00")

# ---------- Alarms Tab ----------
class AlarmsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        self.alarms = []

        self.tree = ttk.Treeview(self, columns=("time", "label"),
                                 show="headings", height=6, bootstyle="info")
        self.tree.heading("time", text="Time")
        self.tree.heading("label", text="Label")
        self.tree.pack(fill=BOTH, expand=YES, pady=10)

        form = ttk.Frame(self)
        form.pack(pady=10)

        self.time_var = tk.StringVar()
        self.label_var = tk.StringVar()

        ttk.Entry(form, textvariable=self.time_var, width=10).pack(side=LEFT, padx=5)
        ttk.Entry(form, textvariable=self.label_var, width=15).pack(side=LEFT, padx=5)

        ttk.Button(form, text="Add Alarm", command=self.add_alarm,
                   bootstyle="success-outline").pack(side=LEFT, padx=5)
        ttk.Button(form, text="Remove Selected", command=self.remove_alarm,
                   bootstyle="danger-outline").pack(side=LEFT, padx=5)

        self.check_alarms()

    def add_alarm(self):
        t = self.time_var.get().strip()
        lbl = self.label_var.get().strip()
        if not t:
            return
        try:
            datetime.datetime.strptime(t, "%H:%M")
        except:
            messagebox.showerror("Error", "Invalid time format (HH:MM)")
            return
        self.tree.insert("", "end", values=(t, lbl))
        self.alarms.append((t, lbl))

    def remove_alarm(self):
        for item in self.tree.selection():
            self.tree.delete(item)

    def check_alarms(self):
        now = datetime.datetime.now().strftime("%H:%M")
        for t, lbl in self.alarms:
            if t == now:
                messagebox.showinfo("Alarm", f"⏰ Alarm: {lbl or t}")
        self.after(30_000, self.check_alarms)  # check every 30s

# ---------- Main App ----------
class BeautyClockApp(ttk.Window):
    def __init__(self, themename="darkly"):
        super().__init__(themename=themename)
        self.title("Beauty Multi-Clock App")
        self.geometry("800x700")

        notebook = ttk.Notebook(self, bootstyle="info")
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Analog Clock Tab
        analog_tab = ttk.Frame(notebook, padding=20)
        self.analog = SmoothAnalog(analog_tab, size=420, fps=60)
        self.analog.pack(expand=YES)
        notebook.add(analog_tab, text="Analog Clock")

        # Digital Clock Tab
        digital_tab = ttk.Frame(notebook, padding=20)
        self.digital_label = ttk.Label(digital_tab, font=("Consolas", 48),
                                       bootstyle="info")
        self.digital_label.pack(expand=YES, pady=50)
        self._update_digital()
        notebook.add(digital_tab, text="Digital Clock")

        # Stopwatch
        notebook.add(StopwatchTab(notebook), text="Stopwatch")

        # Timer
        notebook.add(TimerTab(notebook), text="Timer")

        # Alarms
        notebook.add(AlarmsTab(notebook), text="Alarms")

        # Theme Switcher
        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill=X, side=BOTTOM)
        ttk.Label(bottom, text="Theme:").pack(side=LEFT, padx=5)
        self.theme_var = tk.StringVar(value=themename)
        theme_menu = ttk.Combobox(bottom, textvariable=self.theme_var,
                                  values=ttk.Style().theme_names(),
                                  state="readonly", width=15)
        theme_menu.pack(side=LEFT)
        theme_menu.bind("<<ComboboxSelected>>", self.change_theme)

    def _update_digital(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.digital_label.config(text=now)
        self.after(1000, self._update_digital)

    def change_theme(self, event=None):
        self.style.theme_use(self.theme_var.get())

# ---------- Run ----------
if __name__ == "__main__":
    app = BeautyClockApp(themename="superhero")  # try 'darkly', 'flatly', 'superhero'
    app.mainloop()
