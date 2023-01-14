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


@dataclass
class Estado:
    flujo: str
    nombre: str
    nombre_publico: str
    codigo: str
    descripcion: str


@dataclass
class UnidadDir3:
    nombre: str
    codigo: str


@dataclass
class Relacion:
    organo_gestor: UnidadDir3
    unidad_tramitadora: UnidadDir3
    oficina_contable: UnidadDir3
