"""
Módulo definición de la interfaz FACeClient
"""

from abc import ABC

from . import exceptions as excs
from .objects import FACeResult


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
