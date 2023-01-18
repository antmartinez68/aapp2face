from typer.testing import CliRunner

from aapp2face.cli.main import app

from .constants import TEST_RESPONSES_PATH

runner = CliRunner()


def test_nuevas():
    expected_output = (
        "Número registro:    NUMERO_REGISTRO"
        "Fecha registro:     2014-03-19 10:57:38"
        "Oficina contable:   P00000010"
        "Órgano gestor:      P00000010"
        "Unidad tramitadora: P00000010"
        ""
        "Número registro:    NUMERO_REGISTRO_2"
        "Fecha registro:     2014-03-19 11:05:51"
        "Oficina contable:   P00000010"
        "Órgano gestor:      P00000010"
        "Unidad tramitadora: P00000010"
        ""
        "2 nuevas facturas disponibles"
    )

    result = runner.invoke(
        app, ["--fake-set", TEST_RESPONSES_PATH, "facturas", "nuevas"]
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
