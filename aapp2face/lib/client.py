"""
Módulo definición de la interfaz FACeClient
"""

from abc import ABC, abstractmethod

from . import exceptions as excs
from .objects import FACeResult, PeticionCambiarEstadoFactura


class FACeClient(ABC):
    """Clase base de conexión a FACe"""

    def _verify_result_header(self, result: FACeResult):
        if result.codigo != "0":
            codigo_error: str = result.codigo
            mensaje_error: str = result.descripcion
            cod_seguimiento_error: str = result.codigo_seguimiento
            if cod_seguimiento_error is not None:
                mensaje_error = (
                    f"{mensaje_error} (Código Seguimiento: {cod_seguimiento_error})"
                )
            if codigo_error == "001":
                raise excs.UndefinedError(codigo_error, mensaje_error)
            elif "100" <= codigo_error < "200":
                raise excs.SOAPSecurityException(codigo_error, mensaje_error)
            elif "200" <= codigo_error < "300":
                raise excs.AfirmaVerificationException(codigo_error, mensaje_error)
            elif "400" <= codigo_error <= "900":
                raise excs.FACeManagementException(codigo_error, mensaje_error)
            else:
                raise excs.UndocumentedException(codigo_error, mensaje_error)

    @abstractmethod
    def consultar_estados(self):
        """Consultar la lista de estados que maneja FACe."""

        pass

    @abstractmethod
    def consultar_unidades(self):
        """Consultar las relaciones OG-UT-OC asociadas al RCF."""

        pass

    @abstractmethod
    def solicitar_nuevas_facturas(self, oficina_contable: str):
        """Consultar la lista de facturas en estado 'registrada'."""

        pass

    @abstractmethod
    def descargar_factura(self, numero_registro: str):
        """Descarga de una factura."""

        pass

    @abstractmethod
    def confirmar_descarga_factura(
        self, oficina_contable: str, numero_registro: str, codigo_rcf: str
    ):
        """Confirmar descarga de una factura."""

        pass

    @abstractmethod
    def consultar_factura(self, numero_registro: str):
        """Consultar el estado de una factura."""

        pass

    @abstractmethod
    def consultar_listado_facturas(self, numeros_registro: list[str]):
        """Consultar el estado de varias facturas."""

        pass

    @abstractmethod
    def cambiar_estado_factura(
        self, oficina_contable: str, numero_registro: str, codigo: str, comentario: str
    ):
        """Cambiar el estado de una factura."""

        pass

    @abstractmethod
    def cambiar_estado_listado_facturas(
        self, facturas: list[PeticionCambiarEstadoFactura]
    ):
        """Cambiar el estado de varias facturas."""

        pass

    @abstractmethod
    def consultar_codigo_rcf(self, numero_registro: str):
        """Consultar el código RCF de una factura."""

        pass

    @abstractmethod
    def cambiar_codigo_rcf(self, numero_registro: str, codigo_rcf: str):
        """Cambiar el código RCF de una factura."""

        pass

    @abstractmethod
    def solicitar_nuevas_anulaciones(self, oficina_contable: str):
        """Consultar la lista de facturas en estado 'solicitada anulación'."""

        pass

    @abstractmethod
    def gestionar_solicitud_anulacion_factura(
        self, oficina_contable: str, numero_registro: str, codigo: str, comentario: str
    ):
        """Gestionar la solicitud de anulación de una factura."""

        pass

    @abstractmethod
    def gestionar_solicitud_anulacion_listado_facturas(
        self, facturas: list[PeticionCambiarEstadoFactura]
    ):
        """Gestionar la solicitud de anulación de varias facturas."""

        pass
