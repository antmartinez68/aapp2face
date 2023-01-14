from typer.testing import CliRunner

from aapp2face.cli.main import app

from .constants import TEST_RESPONSES_PATH

runner = CliRunner()


def test_estados():
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Órgano gestor:"
        "  Código: P00000010"
        "  Nombre: Unidad Dir Pruebas 10 (OgP00000010)"
        "Unidad tramitadora:"
        "  Código: P00000010"
        "  Nombre: Unidad Dir Pruebas 10 (UtP00000010)"
        "Oficina contable:"
        "  Código: P00000010"
        "  Nombre: Unidad Dir Pruebas 10 (OcP00000010)"
        ""
        "Órgano gestor:"
        "  Código: P00000010"
        "  Nombre: Unidad Dir Pruebas 10 (OgP00000010)"
        "Unidad tramitadora:"
        "  Código: P00000012"
        "  Nombre: Unidad Dir Pruebas 12 (UtP00000012)"
        "Oficina contable:"
        "  Código: P00000010"
        "  Nombre: Unidad Dir Pruebas 10 (OcP00000010)"
        ""
        "2 relaciones disponibles"
    )

    result = runner.invoke(app, ["--fake-set", TEST_RESPONSES_PATH, "unidades"])
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
