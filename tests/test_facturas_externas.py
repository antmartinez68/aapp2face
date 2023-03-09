from pathlib import Path

import pytest

from aapp2face import FACeConnection, FACeFakeSoapClient
from aapp2face.lib.exceptions import FACeManagementException
from aapp2face.lib.objects import NotificaFactura

TEST_RESPONSES_PATH = "./tests/responses"


@pytest.fixture
def conexion():
    client = FACeFakeSoapClient(Path(TEST_RESPONSES_PATH))
    return FACeConnection(client)


def test_gestionar_solicitud_anulacion_facturas(conexion):
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
