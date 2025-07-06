import os
import sys
import tkinter as tk
import tomllib
from tkinter import messagebox, ttk

import toml
import ttkthemes

from lectures import Lectures

IS_DARWIN = sys.platform.startswith("darwin")


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("Settings")
        self.master = master
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # TOMLファイルのパス
        self.toml_file = os.path.join(os.path.dirname(__file__), "rules.toml")
        self.toml_data = {}

        # GUI要素を初期化
        self.create_widgets()

        # TOMLファイルを読み込み
        self.load_toml()

    def create_widgets(self):
        # --- Make the whole window scrollable ---
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

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="Save", command=self.save_file).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(button_frame, text="Reload", command=self.reset_to_default).pack(
            side=tk.LEFT
        )

        # params section
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

        # checkbox for year filter
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
        ttk.Entry(columns_frame, textvariable=self.student_grade_col_var, width=20).grid(
            row=1, column=1, pady=5
        )

        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, text="Columns name definition of lectures.csv").pack(
            anchor=tk.W
        )

        # columns section
        columns_frame = ttk.Frame(main_frame, padding=10)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(columns_frame, text="Key column").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.key_col_entry = ttk.Entry(columns_frame, width=20)
        self.key_col_entry.grid(row=0, column=1, pady=5)

        ttk.Label(columns_frame, text="Lecture name column").grid(
            row=0, column=2, sticky=tk.W, padx=(50, 10), pady=5
        )
        self.lecture_name_col_entry = ttk.Entry(columns_frame, width=20)
        self.lecture_name_col_entry.grid(row=0, column=3, pady=5)

        ttk.Label(columns_frame, text="Category column").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.category_col_entry = ttk.Entry(columns_frame, width=20)
        self.category_col_entry.grid(row=1, column=1, pady=5)

        ttk.Label(columns_frame, text="Credit column").grid(
            row=1, column=2, sticky=tk.W, padx=(50, 10), pady=5
        )
        self.credit_col_entry = ttk.Entry(columns_frame, width=20)
        self.credit_col_entry.grid(row=1, column=3, pady=5)

        # category section
        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, text="Categories").pack(anchor=tk.W)

        faculty_frame = ttk.Frame(main_frame, padding=10)
        faculty_frame.pack(fill=tk.BOTH, expand=True)
        # get_category_names_button
        ttk.Button(
            faculty_frame, text="Get category names", command=self.get_category_names
        ).grid(row=1, column=1, sticky=tk.EW, padx=(0, 0), pady=(5, 0))

        categories_frame = ttk.Frame(main_frame, padding=10)
        categories_frame.pack(fill=tk.BOTH, expand=True)

        # --- Remove the old categories_frame/canvas/scrollbar code ---
        # Instead, just use a simple frame for categories
        self.scrollable_frame = ttk.Frame(categories_frame)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        ttk.Label(main_frame, text="Secondary categories").pack(anchor=tk.W)
        s_categories_frame = ttk.Frame(main_frame, padding=10)
        s_categories_frame.pack(fill=tk.BOTH, expand=True)

        self.secondary_category_frame = ttk.Frame(s_categories_frame)
        self.secondary_category_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # カテゴリ編集用の変数を格納する辞書
        self.category_vars = {}
        self.secondary_category_vars = {}

    def load_toml(self):
        """TOMLファイルを読み込む"""
        try:
            if os.path.exists(self.toml_file):
                with open(self.toml_file, "rb") as f:
                    self.toml_data = tomllib.load(f)
                self.update_gui()
            else:
                messagebox.showwarning("警告", f"{self.toml_file}が見つかりません")
        except Exception as e:
            messagebox.showerror("エラー", f"TOMLファイルの読み込みに失敗しました: {e}")

    def update_gui(self):
        """GUIを更新"""
        # パラメータの更新
        if "params" in self.toml_data:
            self.target_credits_var.set(
                str(self.toml_data["params"].get("extrapolate_target_credits", "120"))
            )
            self.csv_encoding_var.set(
                self.toml_data["params"].get("csv_encoding", "utf-8")
            )
            self.font_var.set(self.toml_data["params"].get("font_in_report", "Arial"))
            self.year_filter_var.set(
                self.toml_data["params"].get("year_filter", False)
            )

        if "columns_in_students" in self.toml_data:
            self.student_key_col_var.set(
                self.toml_data["columns_in_students"].get("key", "Student ID")
            )
            self.student_name_col_var.set(
                self.toml_data["columns_in_students"].get("name", "Student Name")
            )
            self.student_grade_col_var.set(
                self.toml_data["columns_in_students"].get("grade", "Grade")
            )

        if "columns_in_lectures" in self.toml_data:
            self.key_col_entry.delete(0, tk.END)
            self.key_col_entry.insert(
                0, self.toml_data["columns_in_lectures"].get("key")
            )
            self.lecture_name_col_entry.delete(0, tk.END)
            self.lecture_name_col_entry.insert(
                0, self.toml_data["columns_in_lectures"].get("name")
            )
            self.category_col_entry.delete(0, tk.END)
            self.category_col_entry.insert(
                0, self.toml_data["columns_in_lectures"].get("category")
            )
            self.credit_col_entry.delete(0, tk.END)
            self.credit_col_entry.insert(
                0, self.toml_data["columns_in_lectures"].get("credit")
            )

        # 既存のカテゴリウィジェットをクリア
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.category_vars.clear()
        if "categories" in self.toml_data:
            col = 0
            row = 0
            idx = 0
            for category_name, category_data in self.toml_data["categories"].items():
                self.create_category_widgets(
                    category_name, category_data, row, col, idx
                )
                if col == 0:
                    col = 1
                else:
                    col = 0
                    row += 1
                idx += 1

        for widget in self.secondary_category_frame.winfo_children():
            widget.destroy()
        self.secondary_category_vars.clear()
        if "secondary_categories" in self.toml_data:
            col = 0
            row = 0
            idx = 0
            for category_name, category_data in self.toml_data[
                "secondary_categories"
            ].items():
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
        """カテゴリ用のウィジェットを作成"""
        # カテゴリフレーム
        cat_frame = ttk.Frame(self.scrollable_frame, padding=20, relief="groove")

        cat_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(cat_frame, text=f"{idx}: {category_name}").grid(
            row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )

        # 変数を格納する辞書
        self.category_vars[category_name] = {}

        # 最大単位数
        ttk.Label(cat_frame, text="Max. credits:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10)
        )
        max_credits_var = tk.StringVar(value=str(category_data.get("max_credits", 0)))
        self.category_vars[category_name]["max_credits"] = max_credits_var
        ttk.Entry(cat_frame, textvariable=max_credits_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=(0, 20)
        )

        # カテゴリリスト
        ttk.Label(cat_frame, text="Category:").grid(
            row=2, column=0, sticky=tk.NW, padx=(0, 10), pady=(10, 0)
        )
        category_text = tk.Text(cat_frame, height=4, width=50, relief="flat")
        category_text.grid(row=2, column=1, columnspan=3, sticky="ew", pady=(10, 0))

        # カテゴリリストの内容を設定
        categories = category_data.get("category", [])
        if isinstance(categories, list):
            category_text.insert(tk.END, "\n".join(categories))
        else:
            category_text.insert(tk.END, str(categories))

        self.category_vars[category_name]["category"] = category_text

        # 自コースリスト
        ttk.Label(cat_frame, text="Pooled:").grid(
            row=3, column=0, sticky=tk.NW, padx=(0, 10), pady=(10, 0)
        )
        my_courses_text = tk.Text(cat_frame, height=3, width=50, relief="flat")
        my_courses_text.grid(row=3, column=1, columnspan=3, sticky="ew", pady=(10, 0))

        # 自コースリストの内容を設定
        my_courses = category_data.get("my_courses", [])
        if isinstance(my_courses, list):
            my_courses_text.insert(tk.END, "\n".join(my_courses))
        else:
            my_courses_text.insert(tk.END, str(my_courses))

        self.category_vars[category_name]["my_courses"] = my_courses_text

        # グリッドの重みを設定
        cat_frame.grid_columnconfigure(1, weight=1)

    def create_secondary_category_widgets(
        self, category_name, category_data, row, col, idx
    ):
        """カテゴリ用のウィジェットを作成"""
        cat_frame = ttk.Frame(
            self.secondary_category_frame, padding=20, relief="groove"
        )

        cat_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        self.secondary_category_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(cat_frame, text=f"{idx}: {category_name}").grid(
            row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )

        # 変数を格納する辞書
        self.secondary_category_vars[category_name] = {}
        # 最大単位数
        ttk.Label(cat_frame, text="Max. credits:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10)
        )
        max_credits_var = tk.StringVar(value=str(category_data.get("max_credits", 0)))
        self.secondary_category_vars[category_name]["max_credits"] = max_credits_var
        ttk.Entry(cat_frame, textvariable=max_credits_var, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=(0, 20)
        )

        # category
        ttk.Label(cat_frame, text="Category:").grid(
            row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )
        category_text = tk.Text(cat_frame, height=4, width=50, relief="flat")
        category_text.grid(row=3, column=1, columnspan=3, sticky="ew", pady=(10, 0))
        # categoryの内容を設定
        categories = category_data.get("category", [])
        if isinstance(categories, list):
            category_text.insert(tk.END, "\n".join(categories))
        else:
            category_text.insert(tk.END, str(categories))
        self.secondary_category_vars[category_name]["category"] = category_text

        cat_frame.grid_columnconfigure(1, weight=1)

    def save_file(self):
        """ファイルを保存"""
        try:
            # データを更新
            self.update_toml_data()

            # ファイルに保存
            with open(self.toml_file, "w", encoding="utf-8") as f:
                toml.dump(self.toml_data, f)

            messagebox.showinfo("成功", "ファイルが保存されました")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました: {e}")

    def update_toml_data(self):
        """GUIからデータを更新"""
        # パラメータを更新
        if "params" not in self.toml_data:
            self.toml_data["params"] = {}

        self.toml_data["params"]["extrapolate_target_credits"] = (
            self.target_credits_var.get() or "120"
        )
        self.toml_data["params"]["csv_encoding"] = (
            self.csv_encoding_var.get() or "utf-8"
        )
        self.toml_data["params"]["font_in_report"] = self.font_var.get() or "Arial"
        self.toml_data["params"]["year_filter"] = self.year_filter_var.get()
        
        # columns_in_students
        if "columns_in_students" not in self.toml_data:
            self.toml_data["columns_in_students"] = {}

        self.toml_data["columns_in_students"]["key"] = (
            self.student_key_col_var.get() or "Student ID"
        )
        self.toml_data["columns_in_students"]["name"] = (
            self.student_name_col_var.get() or "Student Name"
        )
        self.toml_data["columns_in_students"]["grade"] = (
            self.student_grade_col_var.get() or "Grade"
        )

        # columns_in_lectures
        if "columns_in_lectures" not in self.toml_data:
            self.toml_data["columns_in_lectures"] = {}
        self.toml_data["columns_in_lectures"]["key"] = self.key_col_entry.get()
        self.toml_data["columns_in_lectures"]["name"] = (
            self.lecture_name_col_entry.get() or "Lecture Name"
        )
        self.toml_data["columns_in_lectures"]["category"] = (
            self.category_col_entry.get() or "Category"
        )
        self.toml_data["columns_in_lectures"]["credit"] = self.credit_col_entry.get()

        # カテゴリを更新
        if "categories" not in self.toml_data:
            self.toml_data["categories"] = {}

        for category_name, vars_dict in self.category_vars.items():
            category_data = {}

            # 最大単位数
            try:
                category_data["max_credits"] = int(vars_dict["max_credits"].get())
            except ValueError:
                category_data["max_credits"] = 0

            # カテゴリリスト
            category_text = vars_dict["category"].get(1.0, tk.END).strip()
            if category_text:
                category_data["category"] = [
                    line.strip() for line in category_text.split("\n") if line.strip()
                ]
            else:
                category_data["category"] = []

            # 自コースリスト
            my_courses_text = vars_dict["my_courses"].get(1.0, tk.END).strip()
            if my_courses_text:
                category_data["my_courses"] = [
                    line.strip() for line in my_courses_text.split("\n") if line.strip()
                ]
            else:
                category_data["my_courses"] = []

            self.toml_data["categories"][category_name] = category_data
        # セカンダリカテゴリを更新
        if "secondary_categories" not in self.toml_data:
            self.toml_data["secondary_categories"] = {}
        for category_name, vars_dict in self.secondary_category_vars.items():
            category_data = {}

            # 最大単位数
            try:
                category_data["max_credits"] = int(vars_dict["max_credits"].get())
            except ValueError:
                category_data["max_credits"] = 0

            # カテゴリリスト
            category_text = vars_dict["category"].get(1.0, tk.END).strip()
            if category_text:
                category_data["category"] = [
                    line.strip() for line in category_text.split("\n") if line.strip()
                ]
            else:
                category_data["category"] = []

            self.toml_data["secondary_categories"][category_name] = category_data

    def get_category_names(self):
        if "columns_in_lectures" in self.toml_data:
            root_path = os.path.dirname(os.path.abspath(__file__))
            lecture_csv_path = os.path.join(root_path, "lectures.csv")
            lec = Lectures(
                self.toml_data,
                lecture_csv_path,
            )
            categories = lec.get_category_names(
                self.toml_data["columns_in_lectures"]["category"]
            )
            # remove np.nan or empty categories
            categories = [str(cat) for cat in categories if cat and str(cat) != "nan"]

            # open a new window to display categories
            category_window = tk.Toplevel(self.master)
            category_window.title("Categories")
            category_window.geometry("400x500+300+100")
            category_text = tk.Text(category_window, wrap=tk.WORD, relief="flat")
            category_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            category_text.insert(tk.END, "\n".join(categories))

    def reset_to_default(self):
        self.load_toml()

    def close(self):
        """ウィンドウを閉じる"""
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
