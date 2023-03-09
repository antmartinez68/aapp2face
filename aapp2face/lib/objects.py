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


@dataclass
class ConsultarEstadoFactura:
    codigo: str
    descripcion: str
    motivo: str


@dataclass
class ConsultarFactura:
    numero_registro: str
    tramitacion: ConsultarEstadoFactura
    anulacion: ConsultarEstadoFactura


@dataclass
class FACeItemResult:
    """Clase para resultados por elemento en arrays devueltos por FACe.

    Attributes
    ----------
        codigo : str
            Código de resultado devuelto por FACe.
        descripcion : str
            Descripción asociada al resultado devuelto por FACe.
        id : str
            Identificador de referencia en la operación que provocó el
            resultado. Por ejemplo un número de registro de una factura.
    """

    codigo: str
    descripcion: str
    id: str


@dataclass
class CambiarEstadoFactura:
    """Clase para respuesta FACe al cambiar estado de una factura.

    Attributes
    ----------
        numero_registro : str
            Número de registro de la factura dentro de FACe.
        codigo : str
            Identificador del código de estado asignado.
    """

    numero_registro: str
    codigo: str


@dataclass
class PeticionCambiarEstadoFactura:
    """Clase para peticiones FACe al cambiar estado de un listado de facturas.

    Attributes
    ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable.
        numero_registro : str
            Número de registro de la factura dentro de FACe.
        codigo : str
            Identificador del código de estado a asignar.
        comentario : str
            Comentario asociado al cambio de estado de la factura.
    """

    oficina_contable: str
    numero_registro: str
    codigo: str
    comentario: str


@dataclass
class NuevaAnulacion:
    numero_registro: str
    oficina_contable: str
    organo_gestor: str
    unidad_tramitadora: str
    fecha_hora_solicitud: str
    motivo: str


@dataclass
class GestionarSolicitudAnulacionFactura:
    """Clase para respuesta FACe al gestionar solicitud anulación de una factura.

    Attributes
    ----------
        numero_registro : str
            Número de registro de la factura dentro de FACe.
        codigo : str
            Identificador del código de estado asignado.
    """

    numero_registro: str
    codigo: str


@dataclass
class PeticionSolicitudAnulacionListadoFactura:
    """Clase para peticiones FACe al gestionar la solicitud de anulación de un listado de facturas.

    Attributes
    ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable.
        numero_registro : str
            Número de registro de la factura dentro de FACe.
        codigo : str
            Identificador del código de estado a asignar.
        comentario : str
            Comentario asociado a la gestión de la solicitud de
            anulación.
    """

    oficina_contable: str
    numero_registro: str
    codigo: str
    comentario: str


@dataclass
class EstadoCesion:
    """Clase para peticiones FACe al cambiar estado de un listado de facturas.

    Attributes
    ----------
        numero_registro : str
            Número de registro de la factura dentro de FACe.
        codigo : str
            Identificador del código de estado de la cesión.
        comentario : str
            Comentario asociado al estado de cesión de la factura.
    """

    numero_registro: str
    codigo: str
    comentario: str


@dataclass
class DatosSolicitante:
    """Clase para datos solicitante en peticiones FACe para obtener documento de cesión.

    Attributes
    ----------
        nif : str
            NIF del solicitante para obtener documento de cesión.
        nombre : str
            Nombre del solicitante para obtener documento de cesión.
        apellidos : str
            Apellidos del solicitante para obtener documento de cesión.
    """

    nif: str
    nombre: str
    apellidos: str


@dataclass
class DocumentoCesion:
    """Clase equivalente al parámetro DocumentoCesion en respuestas FACe"""

    numero_registro: str
    documento: str
    nombre: str
    mime: str

    def guardar(self, path: Path = None, force: bool = False) -> None:
        """Crea un archivo con el documento de la cesión.

        Parameters
        ----------
        path : str, optional
            Ruta donde se guardará el documento decodificada.
        force : bool, optional
            Sobrescribe el archivo si existe. En caso contrario lanza
            una excepción. Por defecto False.
        """
        decoded_data = base64.b64decode(self.documento)
        if force:
            mode = "wb"
        else:
            mode = "xb"
        with open(Path(path, self.nombre), mode) as file:
            file.write(decoded_data)


@dataclass
class GestionarCesion:
    """Clase para respuesta FACe al gestionar una cesión de crédito.

    Attributes
    ----------
        numero_registro : str
            Número de registro de la factura dentro de FACe.
        codigo : str
            Identificador del código de estado de la cesión.
        comentario : str
            Comentario asociado al estado de la cesión de crédito.
    """

    numero_registro: str
    codigo: str
    comentario: str


@dataclass
class NotificaFactura:
    """Clase para respuesta FACe al notificar una factura recibida en otro PGEFe.

    Attributes
    ----------
        numero_registro : str
            Número de registro de la factura dentro de FACe.
        fecha_hora_registro : str
            Fecha de registro en el REC.
    """

    numero_registro: str
    fecha_hora_registro: str
