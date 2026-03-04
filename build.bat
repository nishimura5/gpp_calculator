uv pip install -e .
uv run pyinstaller --onefile --windowed --clean --path src --collect-all gpp_calculator -n "GPT Score" --icon=./src/gpp_calculator/img/icon.ico --version-file=app.version ./scripts/launch_calculator.py
