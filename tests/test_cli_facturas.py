import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aapp2face.cli.main import app

from .constants import TEST_RESPONSES_PATH
from .helpers import md5sum

runner = CliRunner()


@pytest.fixture
def temporary_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temporary_file():
    yield tempfile.NamedTemporaryFile().name


def test_nuevas():
    expected_output = (
        "Número registro:    202001020718"
        "Fecha registro:     2014-03-19 10:57:38"
        "Oficina contable:   P00000010"
        "Órgano gestor:      P00000010"
        "Unidad tramitadora: P00000010"
        ""
        "Número registro:    202001020719"
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


def test_nuevas_error_oficina_no_existente():
    oficina_contable = "P99999999"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Error 411: No existe o inactiva la Oficina Contable asociado al código '{oficina_contable}'."
    )

    result = runner.invoke(
        app,
        ["--fake-set", TEST_RESPONSES_PATH, "facturas", "nuevas", oficina_contable],
    )
    assert result.exit_code == 4
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_nuevas_export(temporary_file):
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "2 nuevas facturas disponibles"
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "facturas",
            "nuevas",
            "--export",
            temporary_file,
        ],
    )

    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_descargar_factura(temporary_dir):
    numero_registro = "202001020718"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Núm. Registro: 202001020718"
        "Núm. Factura:  000000B18"
        "Serie:         None"
        "Importe:       63.13"
        "Proveedor:     A82735122"
        "Archivo:       sample-factura-firmada-32v1.xsig"
        "Anexos:        anexo_1.pdf"
        ""
        "1 facturas descargadas"
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "--download-dir",
            temporary_dir,
            "facturas",
            "descargar",
            numero_registro,
        ],
    )

    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
    assert (
        md5sum(
            Path(temporary_dir)
            .joinpath(numero_registro)
            .joinpath("sample-factura-firmada-32v1.xsig")
        )
        == "2f1d9e07888f0e97f48f35f32e998d3b"
    )
    assert (
        md5sum(Path(temporary_dir).joinpath(numero_registro).joinpath("anexo_1.pdf"))
        == "36e15cfd5f79bfad2fb03436aa503a82"
    )


def test_descargar_factura_export(temporary_dir, temporary_file):
    numero_registro = "202001020718"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "1 facturas descargadas"
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "--download-dir",
            temporary_dir,
            "facturas",
            "descargar",
            "--export",
            temporary_file,
            numero_registro,
        ],
    )

    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_descargar_factura_aviso_documento_no_sobrescrito(temporary_dir):
    numero_registro = "202001020718"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Aviso: El archivo sample-factura-firmada-32v1.xsig ya existe, no será sobrescrito."
        ""
        "Aviso: El archivo anexo_1.pdf ya existe, no será sobrescrito."
        ""
        f"Núm. Registro: {numero_registro}"
        "Núm. Factura:  000000B18"
        "Serie:         None"
        "Importe:       63.13"
        "Proveedor:     A82735122"
        "Archivo:       sample-factura-firmada-32v1.xsig"
        "Anexos:        anexo_1.pdf"
        ""
        "1 facturas descargadas"
    )

    Path(temporary_dir).joinpath(numero_registro).mkdir()
    Path(temporary_dir).joinpath(numero_registro).joinpath(
        "sample-factura-firmada-32v1.xsig"
    ).touch()
    Path(temporary_dir).joinpath(numero_registro).joinpath("anexo_1.pdf").touch()

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "--download-dir",
            temporary_dir,
            "facturas",
            "descargar",
            numero_registro,
        ],
    )

    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_descargar_todas_las_facturas_nuevas(temporary_dir):
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Núm. Registro: 202001020718"
        "Núm. Factura:  000000B18"
        "Serie:         None"
        "Importe:       63.13"
        "Proveedor:     A82735122"
        "Archivo:       sample-factura-firmada-32v1.xsig"
        "Anexos:        anexo_1.pdf"
        ""
        "Núm. Registro: 202001020719"
        "Núm. Factura:  000000B19"
        "Serie:         None"
        "Importe:       1815.65"
        "Proveedor:     A82735122"
        "Archivo:       another-sample-factura-firmada-32v1.xsig"
        "Anexos:        another_anexo_1.pdf"
        ""
        "2 facturas descargadas"
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "--download-dir",
            temporary_dir,
            "facturas",
            "descargar",
        ],
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


def test_consultar_rcf():
    numero_registro = "202001020718"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Código RCF: 230501/F/2014"
    )

    result = runner.invoke(
        app, ["--fake-set", TEST_RESPONSES_PATH, "facturas", "rcf", numero_registro]
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_consultar_rcf_factura_sin_codigo():
    numero_registro = "202001017112"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Factura sin código RCF"
    )

    result = runner.invoke(
        app, ["--fake-set", TEST_RESPONSES_PATH, "facturas", "rcf", numero_registro]
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_consultar_rcf_error():
    numero_registro = "9999"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        "Error 555: No existe archivo con respuesta para simular la petición ('consultarCodigoRCF.9999.json')."
    )

    result = runner.invoke(
        app, ["--fake-set", TEST_RESPONSES_PATH, "facturas", "rcf", numero_registro]
    )
    assert result.exit_code == 4
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_cambiar_rcf():
    numero_registro = "202001020718"
    codigo_rcf = "1234"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Código RCF: {codigo_rcf}"
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "facturas",
            "crcf",
            numero_registro,
            codigo_rcf,
        ],
    )
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")


def test_cambiar_rcf_error():
    numero_registro = "9999"
    codigo_rcf = "1234"
    expected_output = (
        "Aviso: Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
        f"Error 555: No existe archivo con respuesta para simular la petición ('cambiarCodigoRCF.{numero_registro}.json')."
    )

    result = runner.invoke(
        app,
        [
            "--fake-set",
            TEST_RESPONSES_PATH,
            "facturas",
            "crcf",
            numero_registro,
            codigo_rcf,
        ],
    )
    assert result.exit_code == 4
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
