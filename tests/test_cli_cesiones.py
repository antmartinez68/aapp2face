from typer.testing import CliRunner

from aapp2face.cli.main import app

from .constants import TEST_RESPONSES_PATH

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
