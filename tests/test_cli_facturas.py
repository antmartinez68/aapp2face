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


def test_consultar_facturas():
    numero_registro_1 = "202001020718"
    numero_registro_2 = "9999"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Número registro: {numero_registro_1}"
        "Tramitación:"
        "  Código:        1200"
        "  Descripción:   La factura ha sido registrada en el registro electrónico REC"
        "  Motivo:        None"
        "Anulación:"
        "  Código:        4100"
        "  Descripción:   No solicitada anulación"
        "  Motivo:        None"
        ""
        f"Número registro: {numero_registro_2}"
        "  Error: 511 La factura no existe o no tiene permisos."
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "facturas",
            "consultar",
            numero_registro_1,
            numero_registro_2,
        ],
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_consultar_facturas_error():
    numero_registro = "9999"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Error 555: No existe archivo con respuesta para simular la petición ('consultarListadoFacturas.{numero_registro}.json')."
    )

    result = runner.invoke(
        app,
        ["--fake-set", TEST_RESPONSES_PATH, "facturas", "consultar", numero_registro],
    )
    assert result.exit_code == 4
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_cambiar_estado_listado_facturas():
    oficina_contable = "P00000010"
    codigo = "1400"
    comentario = ""
    numero_registro_1 = "202001020718"
    numero_registro_2 = "202001017112"
    numero_registro_3 = "9999"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Número de registro: 202001020718"
        f"Código de estado:   {codigo}"
        ""
        "Número de registro: 202001017112"
        "  Error: 505 Esta transición no esta permitida a través de este web service."
        ""
        "Número de registro: 9999"
        "  Error: 501 No se han encontrado facturas asociadas de la oficina contable al RCF."
        ""
        "1 cambios correctos y 2 errores."
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "facturas",
            "estado",
            oficina_contable,
            codigo,
            comentario,
            numero_registro_1,
            numero_registro_2,
            numero_registro_3,
        ],
    )

    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
