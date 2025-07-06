import os
import tomllib

import toml


class Rules:
    def __init__(self):
        self.toml = None
        root_path = os.path.dirname(os.path.abspath(__file__))
        self.rules_toml_path = os.path.join(root_path, "rules.toml")

    def load_rules(self):
        if not os.path.exists(self.rules_toml_path):
            self._generate_rules()
        with open(self.rules_toml_path, "rb") as f:
            toml = tomllib.load(f)
        self.toml = toml
        if "params" not in toml:
            toml["params"] = {}
        if "columns_in_students" not in toml:
            toml["columns_in_students"] = {}
        if "columns_in_lectures" not in toml:
            toml["columns_in_lectures"] = {}
        if "font_in_report" in toml.get("params", {}):
            self._check_font_exist(toml["params"]["font_in_report"])

    def set_toml(self, toml):
        self.toml = toml

    def get_toml(self):
        if self.toml is None:
            raise ValueError("TOML data is not set. Please load or set TOML data first.")
        return self.toml

    def save_rules(self):
        if self.toml is None:
            raise ValueError("TOML data is not set.")
        with open(self.rules_toml_path, "w") as f:
            f.write(toml.dumps(self.toml))

    def get_extrapolate_target_credits(self):
        return self.toml["params"].get("extrapolate_target_credits", 100)

    def get_font_in_report(self):
        return self.toml["params"].get("font_in_report", "Arial")

    def get_csv_encoding(self):
        return self.toml["params"].get("csv_encoding", "utf-8")

    def get_year_filter(self):
        return self.toml["params"].get("year_filter", False)

    def get_student_rules(self):
        res = {
            "key_column": self.toml["columns_in_students"].get("key", "Student ID"),
            "name_column": self.toml["columns_in_students"].get("name", "Student name"),
            "grade_column": self.toml["columns_in_students"].get("grade", "Grade"),
        }
        return res

    def get_lecture_rules(self):
        res = {
            "key_column": self.toml["columns_in_lectures"].get("key", "Lecture ID"),
            "name_column": self.toml["columns_in_lectures"].get("name", "Lecture name"),
            "category_column": self.toml["columns_in_lectures"].get(
                "category", "Category"
            ),
            "credit_column": self.toml["columns_in_lectures"].get("credit", "Credits"),
        }
        return res

    def get_categories(self):
        return self.toml.get("categories", {})

    def get_secondaty_categories(self):
        return self.toml.get("secondary_categories", {})

    def _check_font_exist(self, font_name):
        from tkinter import font

        available_fonts = font.families()
        if font_name not in available_fonts:
            print(f"Font '{font_name}' is not available on this system.")
            print(available_fonts)

    def _generate_rules(self):
        print("Generating default rules.toml file...")
        with open(self.rules_toml_path, "w") as f:
            f.write("[params]\n")
            f.write("[columns_in_students]\n")
            f.write("[columns_in_lectures]\n")
