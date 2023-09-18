import pathlib
from dataclasses import dataclass
from typing import Any

import click
from benedict import benedict
from rich.console import Console, RenderableType
from rich.table import Table
from rich.text import Text

console = Console()


@click.command("compare-lockfile-versions")
@click.argument("lockfiles", nargs=-1, type=click.Path(path_type=pathlib.Path))
def compare_lockfile_versions_cli(*args: Any, **kwargs: Any) -> None:
    """
    Compare the versions of packages specified in PDM lockfiles.

    The only way to use, currently, is to provide all of the lockfile you wish to have compared.
    The result will be a nice-looking table containing the versions of each, viewable side-by-side of each
    other, such as to allow you to see the differences.

    This cannot be used automatically, unless you wish to simply have a report.
    """
    compare_lockfile_versions(*args, **kwargs)


def compare_lockfile_versions(lockfiles: tuple[pathlib.Path, ...]) -> None:  # noqa: D103
    packages: dict[str, dict[str, PackageData]] = {}
    for lockfile in lockfiles:
        lockfile_content = benedict(lockfile, format="toml")
        for package in lockfile_content.get_list("package"):
            packages.setdefault(package["name"], {})[lockfile.name] = PackageData(
                version=package["version"],
                is_editable=package.get("editable", False),
                path=package.get("path", None),
            )

    table = Table(
        "Package Name",
        *(str(lockfile) for lockfile in lockfiles),
        show_lines=True,
    )
    for package_name, package_lockfiles in packages.items():
        # The first value in the value row is the package name, with the version following after.
        values: list[RenderableType] = [Text(package_name, "bold green")]
        for lockfile in lockfiles:
            if lockfile.name not in package_lockfiles:
                values.append("")  # To have an "empty" table cell.
                continue

            package_data = package_lockfiles[lockfile.name]
            values.append(
                Text(package_data.version, "bold")
                if not package_data.is_editable
                else Text.assemble(
                    (package_data.version, "bold"),
                    " ",
                    ("(editable)", "italic dim"),
                )
            )
        table.add_row(*values)

    console.print(table)


@dataclass(kw_only=True)
class PackageData:
    """Contains relevant data of a package extracted from a PDM lockfile."""

    version: str
    is_editable: bool
    path: str | None = None
