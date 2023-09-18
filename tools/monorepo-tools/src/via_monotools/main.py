# ruff: noqa: D103
from __future__ import annotations

import pathlib
from typing import cast

import click
import tomlkit
from benedict import benedict
from tomlkit.items import Table

from .hook_file import find_hook_file
from .linting import lint_cli
from .pdm import multi_pdm_run_cli


def main() -> None:
    cli()


@click.group("monotools")
def cli() -> None:
    pass


cli.add_command(lint_cli)
cli.add_command(multi_pdm_run_cli)


@cli.command("repo-root")
def cli_config_file() -> None:
    hook_file = find_hook_file()
    print(hook_file.path)


@cli.command("configure-project-commands")
def cli_configure_project_commands() -> None:
    current_pyproject_file = pathlib.Path("pyproject.toml")
    if not current_pyproject_file.exists():
        raise click.ClickException("`pyproject.toml` file not found in current directory!")

    hook_file = find_hook_file()

    hook_pyproject = benedict(tomlkit.parse(hook_file.path.read_bytes()))
    current_pyproject = tomlkit.parse(current_pyproject_file.read_bytes())
    scripts_table = _get_scripts_table(current_pyproject)

    for script_name, script_value in hook_pyproject["tool.via-root.project-scripts"].items():
        scripts_table[script_name] = script_value
        scripts_table[script_name].comment("Generated from root configurations.")
    scripts_table.add(tomlkit.nl())

    current_pyproject_file.write_text(current_pyproject.as_string(), "utf-8")


def _get_scripts_table(document: tomlkit.TOMLDocument) -> Table:
    content = benedict(document)
    if "tool.pdm.scripts" not in content:
        scripts_table = tomlkit.table(True)
        content["tool.pdm.scripts"] = scripts_table
        return scripts_table

    return cast(Table, document.item(tomlkit.key(["tool", "pdm", "scripts"])))


if __name__ == "__main__":
    main()
