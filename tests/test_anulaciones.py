from pathlib import Path

import pytest

from aapp2face import FACeConnection, FACeFakeSoapClient
from aapp2face.lib.exceptions import FACeManagementException
from aapp2face.lib.objects import GestionarSolicitudAnulacionFactura

TEST_RESPONSES_PATH = "./tests/responses"


@pytest.fixture
def conexion():
    client = FACeFakeSoapClient(Path(TEST_RESPONSES_PATH))
    return FACeConnection(client)


def test_gestionar_solicitud_anulacion_facturas(conexion):
    oficina_contable = "P00000010"
    numero_registro = "202001020718"
    codigo = "4300"
    comentario = ""

    result = conexion.gestionar_solicitud_anulacion_factura(
        oficina_contable, numero_registro, codigo, comentario
    )

    assert result == GestionarSolicitudAnulacionFactura(numero_registro, codigo)


def test_gestionar_solicitud_anulacion_facturas_error_transicion(conexion):
    oficina_contable = "P00000010"
    numero_registro = "202001020718"
    codigo = "1200"
    comentario = ""

    with pytest.raises(FACeManagementException):
        conexion.gestionar_solicitud_anulacion_factura(
            oficina_contable, numero_registro, codigo, comentario
        )


def test_gestionar_solicitud_anulacion_facturas_error_codigo(conexion):
    oficina_contable = "P00000010"
    numero_registro = "202001020718"
    codigo = "1234"
    comentario = ""

    with pytest.raises(FACeManagementException):
        conexion.gestionar_solicitud_anulacion_factura(
            oficina_contable, numero_registro, codigo, comentario
        )
