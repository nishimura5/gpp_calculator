import os
import sys
from pathlib import Path


def get_runtime_root_path() -> str:
    """Return the writable runtime root directory for bundled and source runs.

    - Source run: package directory.
    - Frozen on Windows/Linux: executable directory.
    - Frozen on macOS .app: directory that contains the .app bundle.
    """
    if not getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(__file__))

    executable_dir = Path(sys.executable).resolve().parent

    if sys.platform.startswith("darwin"):
        # Typical PyInstaller app path:
        # .../<AppName>.app/Contents/MacOS/<binary>
        if (
            len(executable_dir.parts) >= 3
            and executable_dir.parts[-1] == "MacOS"
            and executable_dir.parts[-2] == "Contents"
            and executable_dir.parts[-3].lower().endswith(".app")
        ):
            return str(executable_dir.parents[2])

    return str(executable_dir)
