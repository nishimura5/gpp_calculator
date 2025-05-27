import os
import sys
import tkinter as tk
from tkinter import ttk

import ttkthemes

import app_rules
import calculator

IS_DARWIN = sys.platform.startswith("darwin")


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("GPP Calculator")

        head_frame = ttk.Frame(master)
        head_frame.pack(padx=10, pady=(15, 5), fill=tk.X)
        calc_btn = ttk.Button(
            head_frame, text="Calculate", width=13, command=self.calculate
        )
        calc_btn.pack(padx=5, side=tk.LEFT)

        self.export_btn = ttk.Button(
            head_frame, text="Export", width=13, command=self.export
        )
        self.export_btn.pack(padx=5, side=tk.LEFT)
        self.export_btn["state"] = "disabled"

        setting_btn = ttk.Button(
            head_frame, text="Settings", command=self.open_settings
        )
        setting_btn.pack(padx=5, side=tk.RIGHT)

        # Treeview Frame with Scrollbar
        tree_frame = ttk.Frame(master)
        tree_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("student_id", "gpp", "total_credits", "extrapolate_gpp"),
            show="headings",
        )
        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("gpp", text="Points")
        self.tree.heading("total_credits", text="Total Credits")
        self.tree.heading("extrapolate_gpp", text="Extrapolate Points")
        self.tree.column("student_id", width=150)
        self.tree.column("gpp", width=100)
        self.tree.column("total_credits", width=100)
        self.tree.column("extrapolate_gpp", width=150)
        self.tree.pack(
            padx=(10, 0), pady=(0, 10), fill=tk.BOTH, expand=True, side=tk.LEFT
        )

        self.scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # event binding double click to open log file
        self.tree.bind(
            "<Double-1>",
            lambda event: self.open_log_file(
                self.tree.item(self.tree.selection())["values"][0]
            ),
        )

    def calculate(self):
        self.clear_tree()
        calc_res = calculator.calc_all()
        if calc_res:
            self.export_btn["state"] = "normal"
            self.export_btn["command"] = lambda: self.export(calc_res)
        else:
            self.export_btn["state"] = "disabled"
        for res in calc_res:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    res["student_id"],
                    f"{res['gpp']:.1f}",
                    f"{res['total_credits']:.1f}",
                    f"{res['extrapolate_gpp']:.1f}",
                ),
            )

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.export_btn["state"] = "disabled"
        self.export_btn["command"] = lambda: None

    def export(self):
        pass

    def open_settings(self):
        dlg_modal = tk.Toplevel(self)
        dlg_modal.transient(self.master)
        dlg_modal.geometry("1050x600+100+100")
        dlg_modal.grab_set()
        a = app_rules.App(dlg_modal)
        dlg_modal.protocol(
            "WM_DELETE_WINDOW",
            lambda: [dlg_modal.destroy(), a.close()],
        )
        self.wait_window(dlg_modal)

    def open_log_file(self, student_id):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = "log"
        log_file = os.path.join(current_dir, log_path, f"{student_id}.txt")
        try:
            # 等角フォントを使用
            if IS_DARWIN:
                font = ("Menlo", 11)
            else:
                font = ("MS Gothic", 11)
            with open(log_file, "r", encoding="utf-8") as f:
                log_content = f.read()
            dlg_modal = tk.Toplevel(self)
            dlg_modal.transient(self.master)
            dlg_modal.geometry("1300x900+100+100")
            dlg_modal.title(f"{student_id}")
            dlg_modal.grab_set()
            text_widget = tk.Text(dlg_modal, wrap=tk.WORD, font=font)
            text_widget.insert(tk.END, log_content)
            text_widget.pack(expand=True, fill=tk.BOTH)
            text_widget.config(state=tk.DISABLED)
            dlg_modal.protocol(
                "WM_DELETE_WINDOW",
                lambda: [dlg_modal.destroy()],
            )
        except FileNotFoundError:
            print(f"Log file {log_file} not found.")


def quit(root):
    root.quit()
    root.destroy()


def main():
    bg_color = "#e8e8e8"
    root = ttkthemes.ThemedTk(theme="breeze")
    root.geometry("1400x700+50+50")
    root.configure(background=bg_color)
    root.option_add("*background", bg_color)
    root.option_add("*Canvas.background", bg_color)
    root.option_add("*Text.background", "#fcfcfc")
    #    root.tk.call("wm", "iconphoto", root._w, tk.PhotoImage(data=icon_data.icon_data))
    s = ttk.Style(root)
    s.configure(".", background=bg_color)
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", lambda: quit(root))
    app.mainloop()


if __name__ == "__main__":
    main()
