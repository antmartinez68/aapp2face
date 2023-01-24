"""
Módulo de clases para estructuras de datos
"""

import base64
from dataclasses import dataclass
from pathlib import Path


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


@dataclass
class NuevaFactura:
    numero_registro: str
    oficina_contable: str
    organo_gestor: str
    unidad_tramitadora: str
    fecha_hora_registro: str


@dataclass
class AnexoFactura:
    """Clase equivalente al parámetro AnexoFile en respuestas FACe"""

    anexo: str
    nombre: str
    mime: str

    def guardar(self, path: Path = None, force: bool = False) -> None:
        """Crea un archivo con el anexo decodificado.

        Parameters
        ----------
        path : str, optional
            Ruta donde se guardará el anexo decodificada.
        force : bool, optional
            Sobrescribe el archivo si existe. En caso contrario lanza
            una excepción. Por defecto False.
        """
        decoded_data = base64.b64decode(self.anexo)
        if force:
            mode = "wb"
        else:
            mode = "xb"
        with open(Path(path, self.nombre), mode) as file:
            file.write(decoded_data)


@dataclass
class DescargaFactura:
    numero: str
    serie: str
    importe: str
    proveedor: str
    nombre: str
    factura: str
    mime: str
    anexos: list[AnexoFactura]

    def guardar(self, path: Path = None, force: bool = False) -> None:
        """Crea un archivo con la factura decodificada.

        Parameters
        ----------
        path : str, optional
            Ruta donde se guardará la factura decodificada.
        force : bool, optional
            Sobrescribe el archivo si existe. En caso contrario lanza
            una excepción. Por defecto False.
        """
        decoded_data = base64.b64decode(self.factura)
        if force:
            mode = "wb"
        else:
            mode = "xb"
        with open(Path(path, self.nombre), mode) as file:
            file.write(decoded_data)


@dataclass
class ConfirmaDescargaFactura:
    numero_registro: str
    oficina_contable: str
    codigo: str
