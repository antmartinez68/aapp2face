"""
Módulo principal de la librería AAPP2FACe
"""

from .client import FACeClient
from .objects import (
    AnexoFactura,
    CambiarEstadoFactura,
    ConfirmaDescargaFactura,
    ConsultarEstadoFactura,
    ConsultarFactura,
    DescargaFactura,
    Estado,
    FACeItemResult,
    GestionarSolicitudAnulacionFactura,
    NuevaAnulacion,
    NuevaFactura,
    PeticionCambiarEstadoFactura,
    PeticionSolicitudAnulacionListadoFactura,
    Relacion,
    UnidadDir3,
)


class FACeConnection:
    """Descripción de la Clase"""

    def __init__(self, client: FACeClient):
        self._client = client

    def consultar_estados(self) -> list[Estado]:
        """Devuelve los estados que maneja FACe para la gestión de una factura.

        Existen dos flujos principales, el ordinario y el de anulación.
        El flujo ordinario corresponde al ciclo de vida de la factura, y
        el flujo de anulación corresponde al ciclo de solicitud de
        anulación.
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
        """Devuelve las relaciones OG-UT-OC asociadas al RCF.

        Las relaciones OG-UT-OC obtenidas son las asociadas al RCF que
        firma la petición.
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
        """Devuelve las facturas que se encuentran en estado "registrada".

        El resultado está limitado a un máximo de 500 facturas. Las
        facturas deben ser procesadas para que entren el resto de
        facturas encoladas.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable. Si no se pasa valor
            retornará un listado de las facturas del RCF.
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

        Después de llamar a este método, y una vez comprobada la
        correcta recepción de la factura, el RCF debe llamar al método
        `confirmar_descarga_factura`. Este método de descarga de
        facturas únicamente puede ser invocado para facturas en estado
        "Registrada". En otros casos el servicio web reportará un error.

        Parameters
        ----------
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe a descargar.
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
    ):
        """Confirma la descarga de una factura.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable.
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            cambiar su RCF.
        codigo_rcf : str
            Código del RCF a asignar a la factura.
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
        """Devuelve el estado de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            consultarse su estado.
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

    def consultar_listado_facturas(self, numeros_registro: list[str]):
        """Devuelve el estado de varias facturas.

        El servicio web limita a un máximo de 500 facturas la consulta.

        Parameters
        ----------
        numeros_registro : list[str]
            Números de registro en el REC, identificadores únicos de las
            facturas dentro de la plataforma FACe para las que quiere
            consultarse su estado.
        """

        response = self._client.consultar_listado_facturas(numeros_registro)
        result: list[str] = []
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
    ):
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
            Código DIR3 de la Oficina Contable.
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            cambiar su RCF.
        codigo : str
            Identificador del código de estado a asignar.
        comentario : str
            Comentario asociado al cambio de estado de la factura.
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
    ):
        """Cambia el estado de múltiples facturas.

        Las restricciones que el servicio web presenta para esta
        operación son las mismas aplicadas al método
        `cambiar_estado_factura`.

        El servicio web limita a un máximo de 100 facturas la petición.

        Parameters
        ----------
        facturas : list[PeticionCambiarEstadoFactura]
            Lista de peticiones con los datos de las facturas a cambiar.
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
        """Devuelve el código RCF de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            consultarse su RCF.
        """

        response = self._client.consultar_codigo_rcf(numero_registro)
        if response["codigoRCF"] == None:
            result = ""
        else:
            result = response["codigoRCF"]

        return result

    def cambiar_codigo_rcf(self, numero_registro: str, codigo_rcf: str):
        """Cambia el código RCF de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            cambiar su RCF.
        codigo_rcf : str
            Código del RCF a asignar a la factura.
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
        """Devuelve las facturas que se encuentran en estado "solicitada anulación".

        El resultado está limitado a un máximo de 500 facturas. Las
        solicitudes deben ser procesadas para que entren el resto de
        solicitudes encoladas.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable. Si no se pasa valor
            retornará un listado de las facturas del RCF.
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
    ):
        """Gestiona una solicitud de anulación, aceptándo o rechazando dicha solicitud.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable.
        numero_registro : str
            Número de registro, en el REC, de la factura para la que
            quiere gestionarse su solicitud de anulación.
        codigo : str
            Identificador del código de estado a asignar.
        comentario : str
            Comentario asociado a la gestión de la solicitud de
            anulación.
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
    ):
        """Gestiona la solicitud de anulación de varias facturas.

        El servicio web limita a un máximo de 100 facturas la petición.

        Parameters
        ----------
        facturas : list[PeticionSolicitudAnulacionListadoFactura]
            Lista de peticiones con los datos de las solicitudes de
            anulación a gestionar.
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
