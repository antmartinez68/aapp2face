import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aapp2face.cli.main import app

from .constants import TEST_RESPONSES_PATH
from .helpers import md5sum

runner = CliRunner()


def test_consultar():
    numero_registro = "202001020718"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Número registro: {numero_registro}"
        "Estado:          6200"
        "Comentario:      None"
    )

    result = runner.invoke(
        app,
        ["--fake-set", TEST_RESPONSES_PATH, "cesiones", "consultar", numero_registro],
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_consultar_error_factura_no_existente():
    numero_registro = "202001020719"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Error 501: No se han encontrado facturas asociadas de la oficina contable al RCF."
    )

    result = runner.invoke(
        app,
        ["--fake-set", TEST_RESPONSES_PATH, "cesiones", "consultar", numero_registro],
    )
    assert result.exit_code == 4
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


@pytest.fixture
def temporary_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_documento(temporary_dir):
    csv = "CSV1"
    repositorio = "CGN"
    nif = "99999999R"
    nombre = "NOMBRE"
    apellidos = "APELLIDOS"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Núm. Registro: CSV1"
        "Archivo:       doc-cesion.pdf"
        "Mime:          application/pdf"
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "--download-dir",
            temporary_dir,
            "cesiones",
            "documento",
            csv,
            repositorio,
            nif,
            nombre,
            apellidos,
        ],
    )

    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
    assert (
        md5sum(Path(temporary_dir).joinpath("doc-cesion.pdf"))
        == "3e4d3fa47dfee3a94be616e44d1e5733"
    )


def test_documento_error_obtencion_documento():
    csv = "CSV2"
    repositorio = "CGN"
    nif = "99999999R"
    nombre = "NOMBRE"
    apellidos = "APELLIDOS"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Error 534: Ocurrió un error al obtener el documento de Notarios."
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "cesiones",
            "documento",
            csv,
            repositorio,
            nif,
            nombre,
            apellidos,
        ],
    )

    assert result.exit_code == 4
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_documento_aviso_documento_no_sobrescrito(temporary_dir):
    csv = "CSV1"
    repositorio = "CGN"
    nif = "99999999R"
    nombre = "NOMBRE"
    apellidos = "APELLIDOS"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Aviso: El archivo doc-cesion.pdf ya existe, no será sobrescrito."
        "Núm. Registro: CSV1"
        "Archivo:       doc-cesion.pdf"
        "Mime:          application/pdf"
    )

    Path(temporary_dir).joinpath("doc-cesion.pdf").touch()

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "--download-dir",
            temporary_dir,
            "cesiones",
            "documento",
            csv,
            repositorio,
            nif,
            nombre,
            apellidos,
        ],
    )

    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
