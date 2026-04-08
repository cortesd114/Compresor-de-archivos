from __future__ import annotations

import flet as ft

if __package__ in (None, ""):
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.ui.home_page import build_home_page


def run_app() -> None:
    ft.run(build_home_page)


if __name__ == "__main__":
    run_app()