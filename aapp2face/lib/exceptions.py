"""
Módulo de excepciones
"""


class FACeException(Exception):
    """Clase base para excepciones por errores reportados por FACe"""

    def __init__(self, code: str, msg: str):
        super().__init__(msg)
        self.code = code
        self.msg = msg


class UndefinedError(FACeException):
    """
    El proceso finalizó con error. El error no ha sido determinado, pudo
    deberse a problemas de comunicación con otras plataformas, problemas
    de datos, etc.)
    """


class UndocumentedException(FACeException):
    """Lanzada cuando FACe devuelve un código de resultado no documentado"""


class SOAPSecurityException(FACeException):
    """Lanzada por errores en verificación de seguridad SOAP"""


class AfirmaVerificationException(FACeException):
    """Lanzada por errores en la verificación con Afirma"""


class FACeManagementException(FACeException):
    """Lanzada por errores asociados a la gestión en FACe"""
