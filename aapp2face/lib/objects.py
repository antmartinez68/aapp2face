"""
Módulo de clases para estructuras de datos.
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
        Código de resultado devuelto por FACe
    descripcion : str
        Descripción asociada al resultado devuelto por FACe
    codigo_seguimiento : str
        Código asociado al registro de la llamada. Este código puede
        ser solicitado para resolución de incidencias
    """

    codigo: str
    descripcion: str
    codigo_seguimiento: str


@dataclass
class Estado:
    """Clase para respuesta FACe con datos de cada uno de los estados que maneja

    Attributes
    ----------
    flujo : str
        Flujo al que pertenece el estado
    nombre : str
        Nombre interno del estado
    nombre_publico : str
        Nombre externo del estado
    codigo : str
        Identificador del estado
    descripcion : str
        Descripción del estado
    """

    flujo: str
    nombre: str
    nombre_publico: str
    codigo: str
    descripcion: str


@dataclass
class UnidadDir3:
    """Clase para respuesta FACe con datos de una unidad DIR3

    Attributes
    ----------
    nombre : str
        Nombre de la unidad
    codigo : str
        Código DIR3 de la unidad
    """

    nombre: str
    codigo: str


@dataclass
class Relacion:
    """Clase para respuesta FACe con datos de una relación OG-UT-OC

    Attributes
    ----------
    organo_gestor : UnidadDir3
        Identificación del Órgano Gestor
    unidad_tramitadora : UnidadDir3
        Identificación de la Unidad Tramitadora
    oficina_contable : UnidadDir3
        Identificación de la Oficina Contable
    """

    organo_gestor: UnidadDir3
    unidad_tramitadora: UnidadDir3
    oficina_contable: UnidadDir3


@dataclass
class NuevaFactura:
    """Clase para respuestas FACe al consultar nuevas facturas.

    Attributes
    ----------
    numero_registro : str
        Número de registro de la factura dentro de FACe
    oficina_contable : str
        Código DIR3 de la Oficina Contable
    organo_gestor : str
        Código DIR3 del Órgano Gestor
    unidad_tramitadora : str
        Código DIR3 de la Unidad Tramitadora
    fecha_hora_registro : str
        Fecha y hora de registro de la factura
    """

    numero_registro: str
    oficina_contable: str
    organo_gestor: str
    unidad_tramitadora: str
    fecha_hora_registro: str


@dataclass
class AnexoFactura:
    """Clase para respuesta FACe con anexo a una factura

    Attributes
    ----------
    anexo : str
        Documento del anexo en base64
    nombre : str
        Nombre del archivo del anexo
    mime : str
        Formato del archivo
    """

    anexo: str
    nombre: str
    mime: str

    def guardar(self, path: Path = None, force: bool = False) -> None:
        """Crea un archivo con el anexo decodificado.

        Parameters
        ----------
        path : str, optional
            Ruta donde se guardará el anexo decodificada
        force : bool, optional
            Sobrescribe el archivo si existe. En caso contrario lanza
            una excepción. Por defecto False
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
    """Clase para respuesta FACe con una factura descargada

    Attributes
    ----------
    numero : str
        Número de la factura
    serie : str
        Serie de la factura
    importe : str
        Importe de la factura
    proveedor : str
        Nombre del proveedor
    nombre : str
        Nombre del archivo de la factura
    factura : str
        Documento de la factura en base64
    mime : str
        Formato del archivo
    anexos : list[AnexoFactura]
        Lista de anexos de la factura
    """

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
            Ruta donde se guardará la factura decodificada
        force : bool, optional
            Sobrescribe el archivo si existe. En caso contrario lanza
            una excepción. Por defecto False
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
    """Clase para respuesta FACe al confirmar descarga de una factura.

    Attributes
    ----------
    numero_registro : str
        Número de registro de la factura dentro de FACe
    oficina_contable : str
        Código DIR3 de la Oficina Contable
    codigo : str
        Identificador del estado asignado
    """

    numero_registro: str
    oficina_contable: str
    codigo: str


@dataclass
class ConsultarEstadoFactura:
    """Clase para estado de una factura en FACe dentro de un flujo de tramitación.

    Attributes
    ----------
    codigo : str
        Identificador del estado de una factura
    descripcion : str
        Descripción del código de estado
    motivo : str
        Comentario que se indicó al asignar el estado
    """

    codigo: str
    descripcion: str
    motivo: str


@dataclass
class ConsultarFactura:
    """Clase para respuesta FACe al consultar estado de una factura.

    Attributes
    ----------
    numero_registro : str
        Número de registro de la factura dentro de FACe
    tramitacion : ConsultarEstadoFactura
        Estado de la factura en el flujo ordinario
    anulacion : ConsultarEstadoFactura
        Estado de la factura en el flujo de anulación
    """

    numero_registro: str
    tramitacion: ConsultarEstadoFactura
    anulacion: ConsultarEstadoFactura


@dataclass
class FACeItemResult:
    """Clase para resultados por elemento en arrays devueltos por FACe.

    Attributes
    ----------
    codigo : str
        Código de resultado devuelto por FACe
    descripcion : str
        Descripción asociada al resultado devuelto por FACe
    id : str
        Identificador de referencia en la operación que provocó el
        resultado. Por ejemplo un número de registro de una factura
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
        Número de registro de la factura dentro de FACe
    codigo : str
        Identificador del estado asignado
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
        Identificador del estado a asignar.
    comentario : str
        Comentario asociado al cambio de estado de la factura.
    """

    oficina_contable: str
    numero_registro: str
    codigo: str
    comentario: str


@dataclass
class NuevaAnulacion:
    """Clase para respuestas FACe al consultar las solicitudes de anulación.

    Attributes
    ----------
    numero_registro : str
        Número de registro de la factura dentro de FACe
    oficina_contable : str
        Código DIR3 de la Oficina Contable
    organo_gestor : str
        Código DIR3 del Órgano Gestor
    unidad_tramitadora : str
        Código DIR3 de la Unidad Tramitadora
    fecha_hora_solicitud : str
        Fecha y hora de la solicitud de anulación
    motivo : str
        Motivo de la solicitud de anulación indicada por el proveedor
    """

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
        Número de registro de la factura dentro de FACe
    codigo : str
        Identificador del estado asignado
    """

    numero_registro: str
    codigo: str


@dataclass
class PeticionSolicitudAnulacionListadoFactura:
    """Clase para peticiones FACe al gestionar la solicitud de anulación de un listado de facturas.

    Attributes
    ----------
    oficina_contable : str
        Código DIR3 de la Oficina Contable
    numero_registro : str
        Número de registro de la factura dentro de FACe
    codigo : str
        Identificador del estado a asignar
    comentario : str
        Comentario asociado a la gestión de la solicitud de
        anulación
    """

    oficina_contable: str
    numero_registro: str
    codigo: str
    comentario: str


@dataclass
class EstadoCesion:
    """Clase para repuesta FACe al consultar el estado de una cesión de crédito.

    Attributes
    ----------
    numero_registro : str
        Número de registro de la factura dentro de FACe
    codigo : str
        Identificador del estado de la cesión de crédito
    comentario : str
        Comentario asociado al estado de cesión de crédito
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
        NIF del solicitante para obtener documento de cesión
    nombre : str
        Nombre del solicitante para obtener documento de cesión
    apellidos : str
        Apellidos del solicitante para obtener documento de cesión
    """

    nif: str
    nombre: str
    apellidos: str


@dataclass
class DocumentoCesion:
    """Clase para respuesta FACe con el documento de una cesión de crédito

    Attributes
    ----------
    numero_registro : str
        Número de registro de la factura dentro de FACe
    documento : str
        Documento de la cesión en base64
    nombre : str
        Nombre del documento
    mime : str
        Formato del documento
    """

    numero_registro: str
    documento: str
    nombre: str
    mime: str

    def guardar(self, path: Path = None, force: bool = False) -> None:
        """Crea un archivo con el documento de la cesión.

        Parameters
        ----------
        path : str, optional
            Ruta donde se guardará el documento decodificado
        force : bool, optional
            Sobrescribe el archivo si existe. En caso contrario lanza
            una excepción. Por defecto False
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
        Número de registro de la factura dentro de FACe
    codigo : str
        Identificador del estado de la cesión
    comentario : str
        Comentario asociado al estado de la cesión de crédito
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
        Número de registro de la factura dentro de FACe
    fecha_hora_registro : str
        Fecha de registro en el REC
    """

    numero_registro: str
    fecha_hora_registro: str


@dataclass
class DatosPersonales:
    """Clase para petición FACe al notificar una factura no electrónica.

    Attributes
    ----------
    tipo : str
        Tipo de persona Física o Jurídica. Valores posibles ("F", "J")
    nombre_razon_social : str
        Nombre de la persona física o razón social
    apellido1 : str
        Apellido 1 de la persona jurídica si procede
    apellido2 : str
        Apellido 2 de la persona jurídica si procede
    documento_nacional : str
        DNI de la persona física o jurídica
    """

    tipo: str
    nombre_razon_social: str
    apellido1: str
    apellido2: str
    documento_nacional: str
