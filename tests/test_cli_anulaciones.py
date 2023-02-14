from typer.testing import CliRunner

from aapp2face.cli.main import app

from .constants import TEST_RESPONSES_PATH

runner = CliRunner()


def test_nuevas():
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Número registro:    NUMERO_REGISTRO"
        "Fecha solicitud:    2015-09-08 17:32:00"
        "Oficina contable:   P00000010"
        "Órgano gestor:      P00000010"
        "Unidad tramitadora: P00000010"
        "Motivo:             MOTIVO"
        ""
        "Número registro:    NUMERO_REGISTRO_2"
        "Fecha solicitud:    2015-09-08 17:10:31"
        "Oficina contable:   P00000010"
        "Órgano gestor:      P00000010"
        "Unidad tramitadora: P00000010"
        "Motivo:             MOTIVO"
        ""
        "2 nuevas solicitudes de anulación"
    )

    result = runner.invoke(
        app, ["--fake-set", TEST_RESPONSES_PATH, "anulaciones", "nuevas"]
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_nuevas_anulaciones_oficina_no_existente():
    oficina_contable = "P99999999"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Error 411: No existe o inactiva la Oficina Contable asociado al código '{oficina_contable}'."
    )

    result = runner.invoke(
        app,
        ["--fake-set", TEST_RESPONSES_PATH, "anulaciones", "nuevas", oficina_contable],
    )
    assert result.exit_code == 4
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
