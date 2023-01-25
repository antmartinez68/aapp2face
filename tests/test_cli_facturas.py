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


def test_descargar_factura_ya_confirmada():
    numero_registro = "1111"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Error 502: La factura ya ha sido recibida en destino por el RCF, no se puede descargar ('{numero_registro}')."
        ""
        "0 facturas descargadas"
    )

    result = runner.invoke(
        app,
        ["--fake-set", TEST_RESPONSES_PATH, "facturas", "descargar", numero_registro],
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_confirmar_descarga_factura():
    oficina_contable = "P00000010"
    numero_registro = "202001020718"
    codigo_rcf = "1234"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Oficina contable:   P00000010"
        "Número de registro: 202001020718"
        "Código de estado:   1300"
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "facturas",
            "confirmar",
            oficina_contable,
            numero_registro,
            codigo_rcf,
        ],
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_confirmar_descarga_factura_error():
    oficina_contable = "P00000000"
    numero_registro = "9999"
    codigo_rcf = "1234"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Error 555: No existe archivo con respuesta para simular la petición ('confirmarDescargaFactura.{oficina_contable}.{numero_registro}.json')."
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "facturas",
            "confirmar",
            oficina_contable,
            numero_registro,
            codigo_rcf,
        ],
    )
    assert result.exit_code == 4
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
