def main() -> None:
    import importlib

    mod = importlib.import_module("gpp_calculator.app_calculator")
    if hasattr(mod, "main"):
        mod.main()
