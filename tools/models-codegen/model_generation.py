# pylint: disable=all
import pathlib

import click
import datamodel_code_generator
import httpx
from datamodel_code_generator import (
    DataModelType,
    InputFileType,
    LiteralType,
    PythonVersion,
)
from ruamel.yaml import YAML

yaml = YAML()


def generate_pydantic(model_path: pathlib.Path, output_path: pathlib.Path) -> None:
    """
    Generate pydantic schemas from OpenAPI yaml specification.

    Given a `pathlib.Path` pointing to a path to a yaml file containing an OpenAPI
    schema, generate a Python file containing Pydantic models that'll be saved
    at `output_path`.
    """
    datamodel_code_generator.generate(
        input_=model_path,
        input_file_type=InputFileType.OpenAPI,
        output=output_path,
        output_model_type=DataModelType.PydanticBaseModel,
        target_python_version=PythonVersion.PY_310,
        enum_field_as_literal=LiteralType.All,
        use_union_operator=True,
        use_double_quotes=True,
        use_schema_description=True,
        use_generic_container_types=False,
        use_standard_collections=True,
        allow_extra_fields=True,
        field_constraints=False,
        use_annotated=False,
    )

    file_content = output_path.read_text("utf-8")
    output_path.write_text(
        "\n".join(
            [
                "# pylint: disable=all",
                "# mypy: ignore-errors",
                "# fmt: off",
                "# ruff: noqa",
                "",
                file_content,
            ]
        )
    )


@click.command("model_generation")
@click.option(
    "--pull-enricher-schema/--no-pull-enricher-schema",
    "should_pull_enricher_schema",
    help='Whether to pull "fresh" OpenAPI specs for the enricher service.',
    default=False,
)
def cli(should_pull_enricher_schema: bool) -> None:
    """Generate Pydantic models from stored OpenAPI schemas."""
    generate_pydantic(
        pathlib.Path("models/via/via_api.yaml"),
        pathlib.Path("../../services/via-app/src/via/models/via/via_api.py"),
    )

    generate_pydantic(
        pathlib.Path("models/sofi/sofi_api.yaml"),
        pathlib.Path("../../services/via-app/src/via/models/sofi/sofi_api.py"),
    )

    if should_pull_enricher_schema:
        enricher_openapi = httpx.get(
            "https://lux38x6p3i-vpce-03ae66ea9659ed50a.execute-api.us-east-1.amazonaws.com/integration/openapi.json"
        ).json()

        enricher_api_model_path = pathlib.Path("models/enricher/example_api.yaml")
        with enricher_api_model_path.open("w") as enricher_api_model_file:
            yaml.dump(enricher_openapi, enricher_api_model_file)

    generate_pydantic(
        pathlib.Path("models/enricher/example_api.yaml"),
        pathlib.Path("../../services/via-app/src/via/models/enricher/enricher_api.py"),
    )


if __name__ == "__main__":
    cli()
