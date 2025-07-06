import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

import ttkthemes

import rules_toml
from lectures import Lectures

IS_DARWIN = sys.platform.startswith("darwin")


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("Settings")
        self.master = master
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # TOML file path
        self.toml_file = os.path.join(os.path.dirname(__file__), "rules.toml")
        self.toml_data = rules_toml.Rules()
        self.toml_data.load_rules()

        # Initialize GUI elements
        self.create_widgets()

        self.load_toml()

    def create_widgets(self):
        # Make the whole window scrollable
        canvas = tk.Canvas(self, relief="flat", highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = ttk.Frame(self)
        canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        main_frame.bind("<Configure>", _on_frame_configure)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="Save", command=self.save_file).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(button_frame, text="Reload", command=self.reset_to_default).pack(
            side=tk.LEFT
        )

        # Parameters section
        params_frame = ttk.Frame(main_frame, padding=10)
        params_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(params_frame, text="Credits num for extrapolate:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.target_credits_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.target_credits_var, width=10).grid(
            row=0, column=1, sticky=tk.W
        )

        ttk.Label(params_frame, text="CSV encoding:").grid(
            row=0, column=2, sticky=tk.W, padx=(50, 10)
        )
        self.csv_encoding_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.csv_encoding_var, width=10).grid(
            row=0, column=3, sticky=tk.W
        )

        ttk.Label(params_frame, text="Font in report:").grid(
            row=0, column=4, sticky=tk.W, padx=(50, 10)
        )
        self.font_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.font_var, width=12).grid(
            row=0, column=5, sticky=tk.W
        )

        # Year filter checkbox
        self.year_filter_var = tk.BooleanVar()
        ttk.Checkbutton(
            params_frame,
            text="Use year filter",
            variable=self.year_filter_var,
        ).grid(row=0, column=6, sticky=tk.W, padx=(50, 10))

        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, text="Columns name definition of students.csv").pack(
            anchor=tk.W
        )

        # Student columns section
        columns_frame = ttk.Frame(main_frame, padding=10)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(columns_frame, text="Key column").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.student_key_col_var = tk.StringVar()
        ttk.Entry(columns_frame, textvariable=self.student_key_col_var, width=20).grid(
            row=0, column=1, pady=5
        )

        ttk.Label(columns_frame, text="Student name column").grid(
            row=0, column=2, sticky=tk.W, padx=(50, 10), pady=5
        )
        self.student_name_col_var = tk.StringVar()
        ttk.Entry(columns_frame, textvariable=self.student_name_col_var, width=20).grid(
            row=0, column=3, pady=5
        )

        ttk.Label(columns_frame, text="Grade column").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.student_grade_col_var = tk.StringVar()
        ttk.Entry(
            columns_frame, textvariable=self.student_grade_col_var, width=20
        ).grid(row=1, column=1, pady=5)

        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, text="Columns name definition of lectures.csv").pack(
            anchor=tk.W
        )

        # Lecture columns section
        columns_frame = ttk.Frame(main_frame, padding=10)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(columns_frame, text="Key column").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.lecture_key_col_var = tk.StringVar()
        ttk.Entry(columns_frame, textvariable=self.lecture_key_col_var, width=20).grid(
            row=0, column=1, pady=5
        )

        ttk.Label(columns_frame, text="Lecture name column").grid(
            row=0, column=2, sticky=tk.W, padx=(50, 10), pady=5
        )
        self.lecture_name_col_var = tk.StringVar()
        ttk.Entry(columns_frame, textvariable=self.lecture_name_col_var, width=20).grid(
            row=0, column=3, pady=5
        )
        ttk.Label(columns_frame, text="Category column").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.lecture_category_col_var = tk.StringVar()
        ttk.Entry(
            columns_frame, textvariable=self.lecture_category_col_var, width=20
        ).grid(row=1, column=1, pady=5)

        ttk.Label(columns_frame, text="Credit column").grid(
            row=1, column=2, sticky=tk.W, padx=(50, 10), pady=5
        )
        self.lecture_credit_col_var = tk.StringVar()
        ttk.Entry(
            columns_frame, textvariable=self.lecture_credit_col_var, width=20
        ).grid(row=1, column=3, pady=5)

        # Categories section
        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, text="Categories").pack(anchor=tk.W)

        faculty_frame = ttk.Frame(main_frame, padding=10)
        faculty_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Button(
            faculty_frame, text="Get category names", command=self.get_category_names
        ).grid(row=1, column=1, sticky=tk.EW, padx=(0, 0), pady=(5, 0))

        categories_frame = ttk.Frame(main_frame, padding=10)
        categories_frame.pack(fill=tk.BOTH, expand=True)

        # Simple frame for categories
        self.scrollable_frame = ttk.Frame(categories_frame)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, text="Secondary categories").pack(anchor=tk.W)
        s_categories_frame = ttk.Frame(main_frame, padding=10)
        s_categories_frame.pack(fill=tk.BOTH, expand=True)

        self.secondary_category_frame = ttk.Frame(s_categories_frame)
        self.secondary_category_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Category editing variables
        self.category_vars = {}
        self.secondary_category_vars = {}

    def load_toml(self):
        """Load TOML file"""
        self.toml_data.load_rules()
        self.update_gui()

    def update_gui(self):
        """Update GUI"""
        # Parameters
        self.target_credits_var.set(self.toml_data.get_extrapolate_target_credits())
        self.csv_encoding_var.set(self.toml_data.get_csv_encoding())
        self.font_var.set(self.toml_data.get_font_in_report())
        self.year_filter_var.set(self.toml_data.get_year_filter())

        # Student columns
        student_rules = self.toml_data.get_student_rules()
        self.student_key_col_var.set(student_rules.get("key_column"))
        self.student_name_col_var.set(student_rules.get("name_column"))
        self.student_grade_col_var.set(student_rules.get("grade_column"))

        # Lecture columns
        lecture_rules = self.toml_data.get_lecture_rules()
        self.lecture_key_col_var.set(lecture_rules.get("key_column", "Lecture ID"))
        self.lecture_name_col_var.set(lecture_rules.get("name_column", "Lecture Name"))
        self.lecture_category_col_var.set(
            lecture_rules.get("category_column", "Category")
        )
        self.lecture_credit_col_var.set(lecture_rules.get("credit_column", "Credit"))

        # Category widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.category_vars.clear()
        categories_dict = self.toml_data.get_categories()
        if categories_dict:
            col = 0
            row = 0
            idx = 0
            for category_name, category_data in categories_dict.items():
                self.create_category_widgets(
                    category_name, category_data, row, col, idx
                )
                if col == 0:
                    col = 1
                else:
                    col = 0
                    row += 1
                idx += 1

        # Secondary category widgets
        for widget in self.secondary_category_frame.winfo_children():
            widget.destroy()
        self.secondary_category_vars.clear()
        secondary_categories_dict = self.toml_data.get_secondaty_categories()
        if secondary_categories_dict:
            col = 0
            row = 0
            idx = 0
            for category_name, category_data in secondary_categories_dict.items():
                self.create_secondary_category_widgets(
                    category_name, category_data, row, col, idx
                )
                if col == 0:
                    col = 1
                else:
                    col = 0
                    row += 1
                idx += 1

    def create_category_widgets(self, category_name, category_data, row, col, idx):
        """Create widgets for category"""
        cat_frame = ttk.Frame(self.scrollable_frame, padding=20, relief="groove")

        cat_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(cat_frame, text=f"{idx}: {category_name}").grid(
            row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )

        self.category_vars[category_name] = {}

        ttk.Label(cat_frame, text="Max. credits:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10)
        )
        max_credits_var = tk.StringVar(value=str(category_data.get("max_credits", 0)))
        self.category_vars[category_name]["max_credits"] = max_credits_var
        ttk.Entry(cat_frame, textvariable=max_credits_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=(0, 20)
        )

        ttk.Label(cat_frame, text="Category:").grid(
            row=2, column=0, sticky=tk.NW, padx=(0, 10), pady=(10, 0)
        )
        category_text = tk.Text(cat_frame, height=4, width=50, relief="flat")
        category_text.grid(row=2, column=1, columnspan=3, sticky="ew", pady=(10, 0))

        categories = category_data.get("category", [])
        if isinstance(categories, list):
            category_text.insert(tk.END, "\n".join(categories))
        else:
            category_text.insert(tk.END, str(categories))

        self.category_vars[category_name]["category"] = category_text

        ttk.Label(cat_frame, text="Pooled:").grid(
            row=3, column=0, sticky=tk.NW, padx=(0, 10), pady=(10, 0)
        )
        my_courses_text = tk.Text(cat_frame, height=3, width=50, relief="flat")
        my_courses_text.grid(row=3, column=1, columnspan=3, sticky="ew", pady=(10, 0))

        my_courses = category_data.get("my_courses", [])
        if isinstance(my_courses, list):
            my_courses_text.insert(tk.END, "\n".join(my_courses))
        else:
            my_courses_text.insert(tk.END, str(my_courses))

        self.category_vars[category_name]["my_courses"] = my_courses_text

        cat_frame.grid_columnconfigure(1, weight=1)

    def create_secondary_category_widgets(
        self, category_name, category_data, row, col, idx
    ):
        """Create widgets for secondary category"""
        cat_frame = ttk.Frame(
            self.secondary_category_frame, padding=20, relief="groove"
        )

        cat_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        self.secondary_category_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(cat_frame, text=f"{idx}: {category_name}").grid(
            row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )

        self.secondary_category_vars[category_name] = {}
        ttk.Label(cat_frame, text="Max. credits:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10)
        )
        max_credits_var = tk.StringVar(value=str(category_data.get("max_credits", 0)))
        self.secondary_category_vars[category_name]["max_credits"] = max_credits_var
        ttk.Entry(cat_frame, textvariable=max_credits_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=(0, 20)
        )

        ttk.Label(cat_frame, text="Category:").grid(
            row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )
        category_text = tk.Text(cat_frame, height=4, width=50, relief="flat")
        category_text.grid(row=3, column=1, columnspan=3, sticky="ew", pady=(10, 0))
        categories = category_data.get("category", [])
        if isinstance(categories, list):
            category_text.insert(tk.END, "\n".join(categories))
        else:
            category_text.insert(tk.END, str(categories))
        self.secondary_category_vars[category_name]["category"] = category_text

        cat_frame.grid_columnconfigure(1, weight=1)

    def save_file(self):
        """Save file"""
        try:
            self.update_toml_data()
            self.toml_data.save_rules()
            messagebox.showinfo("Success", "File has been saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def update_toml_data(self):
        """Update data from GUI"""
        toml_data = {}
        if "params" not in toml_data:
            toml_data["params"] = {}

        toml_data["params"]["extrapolate_target_credits"] = (
            self.target_credits_var.get() or "120"
        )
        toml_data["params"]["csv_encoding"] = self.csv_encoding_var.get() or "utf-8"
        toml_data["params"]["font_in_report"] = self.font_var.get() or "Arial"
        toml_data["params"]["year_filter"] = self.year_filter_var.get()

        # Student columns
        if "columns_in_students" not in toml_data:
            toml_data["columns_in_students"] = {}
        toml_data["columns_in_students"]["key"] = self.student_key_col_var.get()
        toml_data["columns_in_students"]["name"] = self.student_name_col_var.get()
        toml_data["columns_in_students"]["grade"] = self.student_grade_col_var.get()

        # Lecture columns
        if "columns_in_lectures" not in toml_data:
            toml_data["columns_in_lectures"] = {}
        toml_data["columns_in_lectures"]["key"] = self.lecture_key_col_var.get()
        toml_data["columns_in_lectures"]["name"] = self.lecture_name_col_var.get()
        toml_data["columns_in_lectures"]["category"] = (
            self.lecture_category_col_var.get()
        )
        toml_data["columns_in_lectures"]["credit"] = self.lecture_credit_col_var.get()

        if "categories" not in toml_data:
            toml_data["categories"] = {}

        for category_name, vars_dict in self.category_vars.items():
            category_data = {}

            try:
                category_data["max_credits"] = int(vars_dict["max_credits"].get())
            except ValueError:
                category_data["max_credits"] = 0

            category_text = vars_dict["category"].get(1.0, tk.END).strip()
            if category_text:
                category_data["category"] = [
                    line.strip() for line in category_text.split("\n") if line.strip()
                ]
            else:
                category_data["category"] = []

            my_courses_text = vars_dict["my_courses"].get(1.0, tk.END).strip()
            if my_courses_text:
                category_data["my_courses"] = [
                    line.strip() for line in my_courses_text.split("\n") if line.strip()
                ]
            else:
                category_data["my_courses"] = []

            toml_data["categories"][category_name] = category_data

        if "secondary_categories" not in toml_data:
            toml_data["secondary_categories"] = {}
        for category_name, vars_dict in self.secondary_category_vars.items():
            category_data = {}

            try:
                category_data["max_credits"] = int(vars_dict["max_credits"].get())
            except ValueError:
                category_data["max_credits"] = 0

            category_text = vars_dict["category"].get(1.0, tk.END).strip()
            if category_text:
                category_data["category"] = [
                    line.strip() for line in category_text.split("\n") if line.strip()
                ]
            else:
                category_data["category"] = []

            toml_data["secondary_categories"][category_name] = category_data
        self.toml_data.set_toml(toml_data)

    def get_category_names(self):
        toml_data = self.toml_data.get_toml()
        if "columns_in_lectures" in toml_data:
            root_path = os.path.dirname(os.path.abspath(__file__))
            lecture_csv_path = os.path.join(root_path, "lectures.csv")
            lec = Lectures(
                toml_data,
                lecture_csv_path,
            )
            categories = lec.get_category_names(
                toml_data["columns_in_lectures"]["category"]
            )
            # Remove empty and NaN categories
            categories = [str(cat) for cat in categories if cat and str(cat) != "nan"]

            # Open a new window to display categories
            category_window = tk.Toplevel(self.master)
            category_window.title("Categories")
            category_window.geometry("400x500+300+100")
            category_text = tk.Text(category_window, wrap=tk.WORD, relief="flat")
            category_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            category_text.insert(tk.END, "\n".join(categories))

    def reset_to_default(self):
        self.load_toml()

    def close(self):
        """Close window"""
        self.master.destroy()


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
    s = ttk.Style(root)
    s.configure(".", background=bg_color)
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", lambda: quit(root))
    app.mainloop()


if __name__ == "__main__":
    main()
