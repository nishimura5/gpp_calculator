import os
import tomllib


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
        self._check_font_exist(toml["params"]["font_in_report"])

    def _check_font_exist(self, font_name):
        from tkinter import font

        available_fonts = font.families()
        if font_name not in available_fonts:
            print(f"Font '{font_name}' is not available on this system.")

    def _generate_rules(self):
        with open(self.rules_toml_path, "w") as f:
            f.write("[params]\n")
            f.write("[columns_in_students]\n")
