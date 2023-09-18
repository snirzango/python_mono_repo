from __future__ import annotations

import pathlib
from dataclasses import dataclass

from benedict import benedict


def find_hook_file() -> HookFile:
    """Find the hook file that signifies the root of the repository."""
    for path in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents]:
        pyproject_file = path.joinpath("pyproject.toml")
        if not pyproject_file.exists():
            continue

        pyproject_content = benedict.from_toml(pyproject_file, keypath_separator="/")
        if "tool/via-root" not in pyproject_content:
            continue

        return HookFile(pyproject_file, pyproject_content)

    raise OSError("Hook file not found.")


@dataclass
class HookFile:
    """Object pretaining the path and data of the `pyproject.toml` file at the root of the repository."""

    path: pathlib.Path
    content: benedict
