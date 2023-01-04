"""
Módulo de clases para estructuras de datos
"""


from dataclasses import dataclass


@dataclass
class FACeResult:
    """Clase para resultados devueltos por FACe.

    Attributes
    ----------
        codigo : str
            Código de resultado devuelto por FACe.
        descripcion : str
            Descripción asociada al resultado devuelto por FACe.
        codigo_seguimiento : str
            Código asociado a la trama de la llamada. Este código puede
            ser solicitado para resolución de incidencias.
    """

    codigo: str
    descripcion: str
    codigo_seguimiento: str
