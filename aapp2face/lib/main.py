"""
Módulo principal de la librería AAPP2FACe
"""

import base64

from .client import FACeClient
from .objects import (
    AnexoFactura,
    CambiarEstadoFactura,
    ConfirmaDescargaFactura,
    ConsultarEstadoFactura,
    ConsultarFactura,
    DatosPersonales,
    DatosSolicitante,
    DescargaFactura,
    DocumentoCesion,
    Estado,
    EstadoCesion,
    FACeItemResult,
    GestionarCesion,
    GestionarSolicitudAnulacionFactura,
    NotificaFactura,
    NuevaAnulacion,
    NuevaFactura,
    PeticionCambiarEstadoFactura,
    PeticionSolicitudAnulacionListadoFactura,
    Relacion,
    UnidadDir3,
)


class FACeConnection:
    """Clase principal de conexión a FACe."""

    def __init__(self, client: FACeClient):
        """Constructor

        Parameters
        ----------
        client : FACeClient
            Conector a usar
        """

        self._client = client

    def consultar_estados(self) -> list[Estado]:
        """Obtiene los estados que maneja FACe para la gestión de una factura.

        Existen dos flujos principales, el ordinario y el de anulación.
        El flujo ordinario corresponde al ciclo de vida de la factura, y
        el flujo de anulación corresponde al ciclo de solicitud de
        anulación.

        Returns
        -------
        list[Estado]
            lista de estados que maneja FACe
        """

        response = self._client.consultar_estados()
        result: list[Estado] = []
        if response["estados"] is not None:
            for estado in response["estados"]["Estado"]:
                result.append(
                    Estado(
                        estado["flujo"],
                        estado["nombre"],
                        estado["nombrePublico"],
                        estado["codigo"],
                        estado["descripcion"],
                    )
                )
        return result

    def consultar_unidades(self) -> list[Relacion]:
        """Obtiene las relaciones OG-UT-OC asociadas al RCF.

        Las relaciones OG-UT-OC obtenidas son las asociadas al RCF que
        firma la petición.

        Returns
        -------
        list[Relacion]
            lista de relaciones OG-UT-OC asociadas al RCF
        """

        response = self._client.consultar_unidades()
        result: list[Relacion] = []
        if response["relaciones"] is not None:
            for relacion in response["relaciones"]["OGUTOC"]:
                organo_gestor = UnidadDir3(
                    relacion["organoGestor"]["nombre"],
                    relacion["organoGestor"]["codigo"],
                )
                unidad_tramitadora = UnidadDir3(
                    relacion["unidadTramitadora"]["nombre"],
                    relacion["unidadTramitadora"]["codigo"],
                )
                oficina_contable = UnidadDir3(
                    relacion["oficinaContable"]["nombre"],
                    relacion["oficinaContable"]["codigo"],
                )
                result.append(
                    Relacion(organo_gestor, unidad_tramitadora, oficina_contable)
                )
        return result

    def solicitar_nuevas_facturas(
        self, oficina_contable: str = ""
    ) -> list[NuevaFactura]:
        """Obtiene las facturas que se encuentran en estado "Registrada".

        El RCF debe usar periódicamente este método para obtener las
        facturas que luego deberá recuperar.

        El resultado está limitado a un máximo de 500 facturas. Las
        facturas deben ser procesadas para que entren el resto de
        facturas encoladas.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable. Si no se pasa valor
            retornará un listado de las facturas del RCF

        Returns
        -------
        list[NuevaFactura]
            lista de facturas que se encuentran en estado "Registrada"
        """

        response = self._client.solicitar_nuevas_facturas(oficina_contable)
        result: list[NuevaFactura] = []
        if response["facturas"] is not None:
            for factura in response["facturas"]["solicitarNuevasFacturas"]:
                result.append(
                    NuevaFactura(
                        factura["numeroRegistro"],
                        factura["oficinaContable"],
                        factura["organoGestor"],
                        factura["unidadTramitadora"],
                        factura["fechaHoraRegistro"],
                    )
                )

        return result

    def descargar_factura(self, numero_registro: str) -> DescargaFactura:
        """Descarga una factura.

        Este método únicamente puede ser invocado para facturas en
        estado "Registrada". En otros casos el servicio web reportará un
        error. Después de llamar a este método, y una vez comprobada la
        correcta recepción de la factura, el RCF debe llamar al método
        `confirmar_descarga_factura`.

        Parameters
        ----------
        numero_registro : str
            Número de registro, en el REC, de la factura a descargar

        Returns
        -------
        DescargaFactura
            estructura que contiene la factura descargada
        """

        response = self._client.descargar_factura(numero_registro)
        factura = response["factura"]

        anexos: list[AnexoFactura] = []
        for anexo in factura["anexos"]["AnexoFile"]:
            anexos.append(AnexoFactura(anexo["anexo"], anexo["nombre"], anexo["mime"]))

        return DescargaFactura(
            factura["numero"],
            factura["serie"],
            factura["importe"],
            factura["proveedor"],
            factura["nombre"],
            factura["factura"],
            factura["mime"],
            anexos,
        )

    def confirmar_descarga_factura(
        self, oficina_contable: str, numero_registro: str, codigo_rcf: str
    ) -> ConfirmaDescargaFactura:
        """Confirma la descarga de una factura.

        Este método es complementario al método `descargar_factura`, es
        decir, el RCF deberá solicitar la confirmación de cada factura
        descargada que se haya completado con éxito, de forma que la
        plataforma FACe pueda realizar todas las acciones relacionadas
        con la descarga de factura por parte del RCF. Dicho método
        actualiza la factura al estado 1300 automáticamente.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable
        numero_registro : str
            Número de registro, en el REC, de la factura para la que
            se quiere confirmar su descarga
        codigo_rcf : str
            Código del RCF a asignar a la factura

        Returns
        -------
        ConfirmaDescargaFactura
            estructura que contiene los datos de la confirmación
        """

        response = self._client.confirmar_descarga_factura(
            oficina_contable, numero_registro, codigo_rcf
        )

        return ConfirmaDescargaFactura(
            response["factura"]["numeroRegistro"],
            response["factura"]["oficinaContable"],
            response["factura"]["codigo"],
        )

    def consultar_factura(self, numero_registro: str) -> ConsultarFactura:
        """Consulta el estado de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro, en el REC, de la factura para la que se
            quiere consultar su estado

        Returns
        -------
        ConsultarFactura
            estructura que contiene los datos del estado de una factura
        """

        response = self._client.consultar_factura(numero_registro)
        factura = response["factura"]

        tramitacion = ConsultarEstadoFactura(
            factura["tramitacion"]["codigo"],
            factura["tramitacion"]["descripcion"],
            factura["tramitacion"]["motivo"],
        )

        anulacion = ConsultarEstadoFactura(
            factura["anulacion"]["codigo"],
            factura["anulacion"]["descripcion"],
            factura["anulacion"]["motivo"],
        )

        result = ConsultarFactura(factura["numeroRegistro"], tramitacion, anulacion)

        return result

    def consultar_listado_facturas(
        self, numeros_registro: list[str]
    ) -> list[ConsultarFactura | FACeItemResult]:
        """Consulta el estado de varias facturas.

        El servicio web limita a un máximo de 500 facturas la consulta.

        Parameters
        ----------
        numeros_registro : list[str]
            Lista de números de registro, en el REC, de las facturas
            para las que se quiere consultar su estado

        Returns
        -------
        list[ConsultarFactura | FACeItemResult]
            lista con el estado de cada factura o incidencia al consultar
        """

        response = self._client.consultar_listado_facturas(numeros_registro)
        result: list[ConsultarFactura | FACeItemResult] = []
        if response["facturas"] is not None:
            for factura in response["facturas"]["consultarListadoFacturas"]:
                if factura["codigo"] == "0":
                    tramitacion = ConsultarEstadoFactura(
                        factura["factura"]["tramitacion"]["codigo"],
                        factura["factura"]["tramitacion"]["descripcion"],
                        factura["factura"]["tramitacion"]["motivo"],
                    )

                    anulacion = ConsultarEstadoFactura(
                        factura["factura"]["anulacion"]["codigo"],
                        factura["factura"]["anulacion"]["descripcion"],
                        factura["factura"]["anulacion"]["motivo"],
                    )

                    result.append(
                        ConsultarFactura(
                            factura["factura"]["numeroRegistro"], tramitacion, anulacion
                        )
                    )
                else:
                    result.append(
                        FACeItemResult(
                            factura["codigo"],
                            factura["descripcion"],
                            factura["factura"]["numeroRegistro"],
                        )
                    )

        return result

    def cambiar_estado_factura(
        self, oficina_contable: str, numero_registro: str, codigo: str, comentario: str
    ) -> CambiarEstadoFactura:
        """Cambia el estado de una factura.

        Los estados 1300 y 3100 no pueden ser asignados mediante este
        método ya que estos estados son asignados de forma automática al
        realizar las operaciones de confirmación de descarga de la
        factura y gestión de la solicitud de anulación respectivamente.
        El estado inicial 1200 tampoco es gestionable mediante este
        método.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable
        numero_registro : str
            Número de registro, en el REC, de la factura para la que se
            quiere cambiar su estado
        codigo : str
            Identificador del estado a asignar
        comentario : str
            Comentario asociado al cambio de estado de la factura

        Returns
        -------
        CambiarEstadoFactura
            estructura que contiene los datos del cambio de estado de la factura
        """

        response = self._client.cambiar_estado_factura(
            oficina_contable, numero_registro, codigo, comentario
        )

        return CambiarEstadoFactura(
            response["factura"]["numeroRegistro"],
            response["factura"]["codigo"],
        )

    def cambiar_estado_listado_facturas(
        self, facturas: list[PeticionCambiarEstadoFactura]
    ) -> list[CambiarEstadoFactura | FACeItemResult]:
        """Cambia el estado de varias facturas.

        Las restricciones que el servicio web presenta para esta
        operación son las mismas aplicadas al método
        `cambiar_estado_factura`.

        El servicio web limita a un máximo de 100 facturas la petición.

        Parameters
        ----------
        facturas : list[PeticionCambiarEstadoFactura]
            Lista de peticiones con los datos de las facturas a cambiar

        Returns
        -------
        list[CambiarEstadoFactura | FACeItemResult]
            lista con el cambio de estado de cada factura o incidencia al cambiar
        """

        response = self._client.cambiar_estado_listado_facturas(facturas)

        result: list[CambiarEstadoFactura | FACeItemResult] = []
        if response["facturas"]["cambiarEstadoListadoFacturas"] is not None:
            for factura in response["facturas"]["cambiarEstadoListadoFacturas"]:
                if factura["codigo"] == "0":
                    result.append(
                        CambiarEstadoFactura(
                            factura["factura"]["numeroRegistro"],
                            factura["factura"]["codigo"],
                        )
                    )
                else:
                    result.append(
                        FACeItemResult(
                            factura["codigo"],
                            factura["descripcion"],
                            factura["factura"]["numeroRegistro"],
                        )
                    )

        return result

    def consultar_codigo_rcf(self, numero_registro: str) -> str:
        """Obtiene el código RCF de una factura registrado en FACe.

        Parameters
        ----------
        numero_registro : str
            Número de registro, en el REC, de la factura para la que se
            quiere consultar su código RCF

        Returns
        -------
        str
            código RCF registrado en FACe para la factura
        """

        response = self._client.consultar_codigo_rcf(numero_registro)
        if response["codigoRCF"] == None:
            result = ""
        else:
            result = response["codigoRCF"]

        return result

    def cambiar_codigo_rcf(self, numero_registro: str, codigo_rcf: str) -> str:
        """Cambia el código RCF de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro, en el REC, de la factura para la que se
            quiere cambiar su código RCF
        codigo_rcf : str
            Código RCF a asignar a la factura

        Returns
        -------
        str
            código RCF asignado a la factura
        """

        response = self._client.cambiar_codigo_rcf(numero_registro, codigo_rcf)
        if response["codigoRCF"] == None:
            result = ""
        else:
            result = response["codigoRCF"]

        return result

    def solicitar_nuevas_anulaciones(
        self, oficina_contable: str = ""
    ) -> list[NuevaAnulacion]:
        """Obtiene las facturas que se encuentran en estado "Solicitada anulación".

        El RCF debe usar periódicamente este método para conocer las
        solicitudes de anulación de facturas realizadas en FACe por parte
        de los proveedores.

        El resultado está limitado a un máximo de 500 facturas. Las
        solicitudes deben ser procesadas para que entren el resto de
        solicitudes encoladas.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable. Si no se pasa valor
            retornará un listado de las facturas del RCF

        Returns
        -------
        list[NuevaAnulacion]
            lista de facturas que se encuentran en estado "Solicitada anulación"
        """

        response = self._client.solicitar_nuevas_anulaciones(oficina_contable)
        result: list[NuevaAnulacion] = []
        if response["facturas"] is not None:
            for factura in response["facturas"]["solicitarNuevasAnulaciones"]:
                result.append(
                    NuevaAnulacion(
                        factura["numeroRegistro"],
                        factura["oficinaContable"],
                        factura["organoGestor"],
                        factura["unidadTramitadora"],
                        factura["fechaHoraSolicitudAnulacion"],
                        factura["motivo"],
                    )
                )

        return result

    def gestionar_solicitud_anulacion_factura(
        self, oficina_contable: str, numero_registro: str, codigo: str, comentario: str
    ) -> GestionarSolicitudAnulacionFactura:
        """Gestiona una solicitud de anulación, aceptando o rechazando dicha solicitud.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable
        numero_registro : str
            Número de registro, en el REC, de la factura para la que
            se quiere gestionar su solicitud de anulación
        codigo : str
            Identificador del estado a asignar
        comentario : str
            Comentario asociado a la gestión de la solicitud de
            anulación

        Returns
        -------
        GestionarSolicitudAnulacionFactura
            estructura que contiene los datos de la gestión de la anulación
        """

        response = self._client.gestionar_solicitud_anulacion_factura(
            oficina_contable, numero_registro, codigo, comentario
        )

        return GestionarSolicitudAnulacionFactura(
            response["factura"]["numeroRegistro"],
            response["factura"]["codigo"],
        )

    def gestionar_solicitud_anulacion_listado_facturas(
        self, facturas: list[PeticionSolicitudAnulacionListadoFactura]
    ) -> list[GestionarSolicitudAnulacionFactura | FACeItemResult]:
        """Gestiona la solicitud de anulación de varias facturas.

        El servicio web limita a un máximo de 100 facturas la petición.

        Parameters
        ----------
        facturas : list[PeticionSolicitudAnulacionListadoFactura]
            Lista de peticiones con los datos de las solicitudes de
            anulación a gestionar

        Returns
        -------
        list[GestionarSolicitudAnulacionFactura | FACeItemResult]
            lista con la gestión de la anulación o incidencia al realizarla
        """

        response = self._client.gestionar_solicitud_anulacion_listado_facturas(facturas)

        result: list[GestionarSolicitudAnulacionFactura | FACeItemResult] = []
        if (
            response["facturas"]["gestionarSolicitudAnulacionListadoFacturas"]
            is not None
        ):
            for factura in response["facturas"][
                "gestionarSolicitudAnulacionListadoFacturas"
            ]:
                if factura["codigo"] == "0":
                    result.append(
                        GestionarSolicitudAnulacionFactura(
                            factura["factura"]["numeroRegistro"],
                            factura["factura"]["codigo"],
                        )
                    )
                else:
                    result.append(
                        FACeItemResult(
                            factura["codigo"],
                            factura["descripcion"],
                            factura["factura"]["numeroRegistro"],
                        )
                    )

        return result

    def consultar_estado_cesion(self, numero_registro: str) -> EstadoCesion:
        """Obtiene el estado de la cesión de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro, en el REC, de la factura para la que
            quiere consultarse el estado de la cesión

        Returns
        -------
        EstadoCesion
            estructura que contiene el estado de la cesión
        """

        response = self._client.consultar_estado_cesion(numero_registro)

        result = EstadoCesion(
            response["cesion"]["numeroRegistro"],
            response["cesion"]["estado"],
            response["cesion"]["comentario"],
        )

        return result

    def obtener_documento_cesion(
        self, csv: str, repositorio: str, solicitante: DatosSolicitante
    ) -> DocumentoCesion:
        """Obtiene el documento de la cesión de una factura.

        Este método permite obtener el documento de la cesión conectando
        al servicio de notarios.

        Parameters
        ----------
        csv : str
            Identificador del documento
        repositorio : str
            Repositorio desde el que se obtiene el documento
        solicitante : DatosSolicitante
            Datos del solicitante (nif, nombre, apellidos)

        Returns
        -------
        DocumentoCesion
            estructura de datos que contiene el documento de la cesión
        """

        dict_solicitante = {
            "nif": solicitante.nif,
            "nombre": solicitante.nombre,
            "apellidos": solicitante.apellidos,
        }

        response = self._client.obtener_documento_cesion(
            csv, repositorio, dict_solicitante
        )

        result = DocumentoCesion(
            response["documento"]["numeroRegistro"],
            response["documento"]["documento"],
            response["documento"]["nombre"],
            response["documento"]["mime"],
        )

        return result

    def gestionar_cesion(
        self, numero_registro: str, codigo: str, comentario: str
    ) -> GestionarCesion:
        """Gestiona una cesión de crédito, aceptando o rechazando dicha cesión.

        Parameters
        ----------
        numero_registro : str
            Número de registro, en el REC, de la factura para la que
            quiere gestionarse la cesión de crédito
        codigo : str
            Identificador del estado a asignar
        comentario : str
            Comentario asociado a la gestión de la cesión de crédito

        Returns
        -------
        GestionarCesion
            estructura que contiene el resultado de la gestión de la cesión
        """

        response = self._client.gestionar_cesion(numero_registro, codigo, comentario)

        return GestionarCesion(
            response["cesion"]["numeroRegistro"],
            response["cesion"]["codigo"],
            response["cesion"]["comentario"],
        )

    def notifica_factura(
        self,
        numero_registro: str,
        fecha_registro: str,
        path_factura: str,
        organo_gestor: str,
        unidad_tramitadora: str,
        oficina_contable: str,
        codigo_rcf: str,
        estado: str,
    ) -> NotificaFactura:
        """Notifica una factura recibida en otro PGEFe.

        Este método permite notificar una factura recibida en otro
        PGEFe. El servicio retorna un número de registro y fecha de
        registro para poder consultar y operar la factura en FACe.

        Parameters
        ----------
        numero_registro : str
            Número de registro del PGEFe
        fecha_registro : str
            Fecha de registro del PGEFe formato en 'YYYY-MM-DDThh:mm:ss'
        path_factura : str
            Ruta local del fichero con la factura, en formato facturae
            3.2 o 3.2.1, a enviar
        organo_gestor : str
            Código DIR3 del Órgano Gestor
        unidad_tramitadora : str
            Código DIR3 de la Unidad Tramitadora
        oficina_contable : str
            Código DIR3 del Oficina Contable
        codigo_rcf : str
            Código asignado dentro del RCF
        estado : str
            Código del estado de la factura

        Returns
        -------
        NotificaFactura
            estructura de datos que contiene un número de registro y
            fecha de registro para poder consultar y operar la factura
            en FACe
        """

        with open(path_factura, "rb") as file:
            factura = base64.b64encode(file.read())

        response = self._client.notifica_factura(
            numero_registro,
            fecha_registro,
            factura,
            organo_gestor,
            unidad_tramitadora,
            oficina_contable,
            codigo_rcf,
            estado,
        )

        return NotificaFactura(
            response["facturas"]["numeroRegistro"],
            response["facturas"]["fechaRegistro"],
        )

    def notifica_factura_no_electronica(
        self,
        numero_registro: str,
        fecha_registro: str,
        emisor: DatosPersonales,
        receptor: DatosPersonales,
        tercero: DatosPersonales,
        numero: str,
        serie: str,
        importe: str,
        fecha_expedicion: str,
        organo_gestor: str,
        unidad_tramitadora: str,
        oficina_contable: str,
        codigo_rcf: str,
        estado: str,
        codigo_cnae: str,
    ) -> NotificaFactura:
        """Notifica una factura no electrónica recibida.

        Este método permite notificar una factura no electrónica
        recibida en el registro administrativo de un Organismo. El
        servicio retorna un número de registro y fecha de registro para
        poder consultar y operar la factura en FACe.

        Parameters
        ----------
        numero_registro : str
            Número de registro del PGEFe
        fecha_registro : str
            Fecha de registro del PGEFe en formato 'YYYY-MM-DDThh:mm:ss'
        emisor : DatosPersonales
            Datos del emisor
        receptor : DatosPersonales
            Datos del receptor
        tercero : DatosPersonales
            Datos del tercero
        numero : str
            Número de la factura
        serie : str
            Serie de la factura
        importe : str
            Importe de la factura
        fecha_expedicion : str
            Fecha de expedición de la factura en formato 'YYYY-MM-DDThh:mm:ss'
        organo_gestor : str
            Código DIR3 del Órgano Gestor
        unidad_tramitadora : str
            Código DIR3 de la Unidad Tramitadora
        oficina_contable : str
            Código DIR3 del Oficina Contable
        codigo_rcf : str
            Código asignado dentro de RCF
        estado : str
            Código del estado de la factura
        codigo_cnae : str
            Código de CNAE de la factura

        Returns
        -------
        NotificaFactura
            estructura de datos que contiene un número de registro y
            fecha de registro para poder consultar y operar la factura
            en FACe.
        """

        emisor_dict = {
            "tipo": emisor.tipo,
            "nombreRazonSocial": emisor.nombre_razon_social,
            "apellido1": emisor.apellido1,
            "apellido2": emisor.apellido2,
            "documentoNacional": emisor.documento_nacional,
        }

        receptor_dict = {
            "tipo": receptor.tipo,
            "nombreRazonSocial": receptor.nombre_razon_social,
            "apellido1": receptor.apellido1,
            "apellido2": receptor.apellido2,
            "documentoNacional": receptor.documento_nacional,
        }

        tercero_dict = {
            "tipo": tercero.tipo,
            "nombreRazonSocial": tercero.nombre_razon_social,
            "apellido1": tercero.apellido1,
            "apellido2": tercero.apellido2,
            "documentoNacional": tercero.documento_nacional,
        }

        response = self._client.notifica_factura_no_electronica(
            numero_registro,
            fecha_registro,
            emisor_dict,
            receptor_dict,
            tercero_dict,
            numero,
            serie,
            importe,
            fecha_expedicion,
            organo_gestor,
            unidad_tramitadora,
            oficina_contable,
            codigo_rcf,
            estado,
            codigo_cnae,
        )

        return NotificaFactura(
            response["facturas"]["numeroRegistro"],
            response["facturas"]["fechaRegistro"],
        )
