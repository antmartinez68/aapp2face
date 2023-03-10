from pathlib import Path

import pytest

from aapp2face import FACeConnection, FACeFakeSoapClient
from aapp2face.lib.objects import DatosPersonales, NotificaFactura

TEST_RESPONSES_PATH = "./tests/responses"


@pytest.fixture
def conexion():
    client = FACeFakeSoapClient(Path(TEST_RESPONSES_PATH))
    return FACeConnection(client)


def test_notifica_factura(conexion):
    numero_registro = "2018-800"
    fecha_registro = "2018-10-09T12:00:00"
    factura = Path(TEST_RESPONSES_PATH).joinpath("sample-factura-firmada-32v1.xsig")
    organo_gestor = "P00000010"
    unidad_tramitadora = "P00000010"
    oficina_contable = "P00000010"
    codigo_rcf = "1234"
    estado = "1300"

    result = conexion.notifica_factura(
        numero_registro,
        fecha_registro,
        factura,
        organo_gestor,
        unidad_tramitadora,
        oficina_contable,
        codigo_rcf,
        estado,
    )

    assert result == NotificaFactura("202001020800", "2018-10-09 14:37:56")


def test_notifica_factura_no_electronica(conexion):
    numero_registro = "2018-900"
    fecha_registro = "2018-10-10T09:00:00"
    emisor = DatosPersonales("F", "JUAN", "LOPEZ", "LOPEZ", "00000000A")
    receptor = DatosPersonales("J", "ORGANISMO AUTONOMO", "", "", "S0000000")
    tercero = DatosPersonales("", "", "", "", "")
    numero = "9500"
    serie = "2018"
    importe = "2521,38"
    fecha_expedicion = "2018-10-09T18:50:00"
    organo_gestor = "P00000010"
    unidad_tramitadora = "P00000010"
    oficina_contable = "P00000010"
    codigo_rcf = "1235"
    estado = "1300"
    codigo_cnae = ""

    result = conexion.notifica_factura_no_electronica(
        numero_registro,
        fecha_registro,
        emisor,
        receptor,
        tercero,
        numero,
        serie,
        importe,
        fecha_expedicion,
        organo_gestor,
        unidad_tramitadora,
        oficina_contable,
        codigo_rcf,
        estado,
        codigo_cnae,
    )

    assert result == NotificaFactura("202001020900", "2018-10-10 11:56:37")
