# ruff: noqa: D103
import os
import shlex
import shutil
from typing import NoReturn

import click

from .hook_file import find_hook_file

_WRAPPER_COMMAND_CONTEXT_SETTINGS = {
    "ignore_unknown_options": True,
    "help_option_names": [],
}


@click.group("lint")
def lint_cli() -> None:
    pass


@lint_cli.command("pylint", context_settings=_WRAPPER_COMMAND_CONTEXT_SETTINGS)
@click.argument("arguments", nargs=-1, type=click.UNPROCESSED)
def cli_pylint(arguments: tuple[str, ...]) -> None:
    hook_file = find_hook_file()
    exec_process("pylint", shlex.quote(f"--rcfile={hook_file.path}"), *arguments)


@lint_cli.command("black", context_settings=_WRAPPER_COMMAND_CONTEXT_SETTINGS)
@click.argument("arguments", nargs=-1, type=click.UNPROCESSED)
def cli_black(arguments: tuple[str, ...]) -> None:
    hook_file = find_hook_file()
    exec_process("black", "--config", shlex.quote(str(hook_file.path)), *arguments)


@lint_cli.command("mypy", context_settings=_WRAPPER_COMMAND_CONTEXT_SETTINGS)
@click.argument("arguments", nargs=-1, type=click.UNPROCESSED)
def cli_mypy(arguments: tuple[str, ...]) -> None:
    hook_file = find_hook_file()
    exec_process("mypy", "--config-file", shlex.quote(str(hook_file.path)), *arguments)


def exec_process(executable: str, *args: str) -> NoReturn:
    absolute_executable_path = shutil.which(executable)
    if not absolute_executable_path:
        raise MissingExecutableException(executable)
    os.execvp(absolute_executable_path, [executable, *args])  # noqa: S606


class MissingExecutableException(Exception):
    """Raised when a required executable is missing from the users' system."""

    def __init__(self, executable: str):
        self.executable = executable
        super().__init__(f"Executable '{executable}' is not found in your PATH.")
