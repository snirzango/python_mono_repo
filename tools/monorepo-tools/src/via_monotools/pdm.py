# ruff: noqa: D103
import os
import pathlib
import shlex
import subprocess

import click
from benedict import benedict
from rich import print  # pylint: disable=redefined-builtin
from rich.rule import Rule

from .hook_file import find_hook_file


@click.command("pdm-run", context_settings={"ignore_unknown_options": True})
@click.option("--cwd", "from_cwd", is_flag=True, default=False)
@click.option("--quit-on-failure/--no-quit-on-failure", default=False)
@click.argument("pdm_script_name", type=str)
@click.argument("arguments", nargs=-1, type=click.UNPROCESSED)
def multi_pdm_run_cli(
    from_cwd: bool,
    quit_on_failure: bool,
    pdm_script_name: str,
    arguments: tuple[str, ...],
) -> None:
    search_root = _get_search_root(from_cwd)

    final_return_code = 0
    for pyproject_file in search_root.glob("**/pyproject.toml"):
        pyproject_content = benedict(pyproject_file, format="toml", keypath_separator="/")

        if pdm_script_name not in pyproject_content.get_dict("tool/pdm/scripts", {}):
            continue

        command = ["pdm", "run", pdm_script_name, *arguments]

        relative_path = pyproject_file.relative_to(search_root)
        pretty_command = shlex.join(command)
        print(Rule(f"[cyan]{relative_path}[/] ([dim]{pretty_command}[/])"))

        return_code = subprocess.call(
            command,  # noqa: S603
            cwd=pyproject_file.parent,
            env=os.environ,
        )

        if final_return_code == 0 and return_code != 0:
            final_return_code = return_code
            if quit_on_failure:
                break

    if final_return_code != 0:
        raise SystemExit(final_return_code)


def _get_search_root(from_cwd: bool) -> pathlib.Path:
    if from_cwd:
        return pathlib.Path.cwd()
    return find_hook_file().path.parent
