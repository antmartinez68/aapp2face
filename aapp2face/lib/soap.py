"""
Implementación de la interfaz FACeClient para conexiones reales
"""

import datetime
from pathlib import Path

import zeep
from lxml import etree
from zeep.plugins import HistoryPlugin

from .client import FACeClient
from .objects import (
    FACeResult,
    PeticionCambiarEstadoFactura,
    PeticionSolicitudAnulacionListadoFactura,
)
from .patch import BinarySignatureTimestamp


class FACeSoapClient(FACeClient):
    """Clase del conector FACe usando SOAP."""

    def __init__(
        self, wsdl: str, cert: str, key: str, debug: bool = False, log_path: str = "."
    ):
        """Constructor

        Parameters
        ----------
        wsdl : str
            Ruta del WSDL del servicio SOAP
        cert : str
            Ruta del archivo que contiene el certificado para firmar las peticiones SOAP
        key : str
            Ruta del archivo que contiene la clave privada del certificado
        debug : bool
            Flag que indica se se guarda registro de peticiones. Default: False
        log_path : str
            Ruta donde se ubicará el registro de peticiones. Default: "."
        """

        self._wsdl = wsdl
        self._cert = cert
        self._key = key
        self._debug = debug
        self._log_path = log_path
        self._connected = False

    def _connect(self) -> None:
        """Crea la conexión SOAP con FACe"""

        if not self._connected:
            if not Path(self._cert).is_file():
                raise FileNotFoundError(f"El fichero del certificado no existe.")
            if not Path(self._key).is_file():
                raise FileNotFoundError(
                    f"El fichero con clave privada del certificado no existe."
                )
            self._history = HistoryPlugin()
            wsse = BinarySignatureTimestamp(self._key, self._cert)
            self._face = zeep.Client(self._wsdl, plugins=[self._history], wsse=wsse)

    def _log_soap(self):
        """Escribe la petición y la respuesta SOAP en un archivo de registro"""

        file = Path(self._log_path).joinpath("soap.log")

        with open(file, "a") as f:
            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{fecha_hora} *** PETICIÓN ***\n\n")
            f.write(
                etree.tostring(
                    self._history.last_sent["envelope"],
                    encoding="unicode",
                    pretty_print=True,
                )
            )
            f.write("\n")

            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{fecha_hora} *** RESPUESTA ***\n\n")
            f.write(
                etree.tostring(
                    self._history.last_received["envelope"],
                    encoding="unicode",
                    pretty_print=True,
                )
            )
            f.write("\n")

    def _log_response(self, nombre_metodo, args, result):
        """Escribe datos en claro de petición y respuesta en un archivo de registro"""

        file = Path(self._log_path).joinpath("responses.log")

        with open(file, "a") as f:
            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            args_str = " ".join([str(elem) for elem in args])
            f.write(
                f"{fecha_hora} *** RESPUESTA A MÉTODO {nombre_metodo} (ARGS: {args_str}) ***\n"
            )
            f.write(f"*** USING: {self._wsdl} ***\n")
            f.write(str(result))
            f.write("\n\n")

    def _llamar_metodo_soap(self, nombre_metodo: str, *args, array_type: str = ""):
        """Llama al método SOAP indicado con los argumentos suministrados."""

        # Asegura la conexión de forma lazy
        self._connect()

        # Verificación llamada con tipo array
        if array_type != "":
            array = self._face.get_type(array_type)
            args = list(args)
            args[0] = array(args[0])

        # Llamada al método especificado
        try:
            soap_method = getattr(self._face.service, nombre_metodo)
            result = soap_method(*args)
            if self._debug:
                self._log_response(nombre_metodo, args, result)
        except Exception as e:
            print("Error:", str(e))
        if self._debug:
            self._log_soap()

        # Gestión de excepciones FACe
        result_header = FACeResult(
            result.resultado.codigo,
            result.resultado.descripcion,
            result.resultado.codigoSeguimiento,
        )
        self._verify_result_header(result_header)

        return result

    def consultar_estados(self):
        """Devuelve la respuesta del método SOAP `consultarEstados`.

        Este método retorna la lista de estados que maneja FACe para la
        gestión de la factura. Existen dos flujos principales, el
        ordinario y el de anulación. El flujo ordinario corresponde al
        ciclo de vida de la factura, y el flujo de anulación corresponde
        al ciclo de solicitud de anulación.
        """

        return self._llamar_metodo_soap("consultarEstados")

    def consultar_unidades(self):
        """Devuelve la respuesta del método SOAP `consultarUnidades`.

        Este método permite consultar las relaciones OG-UT-OC asociadas
        al RCF que firma la petición SOAP.
        """

        return self._llamar_metodo_soap("consultarUnidades")

    def solicitar_nuevas_facturas(self, oficina_contable: str):
        """Devuelve la respuesta del método SOAP `solicitarNuevasFacturas`.

        Este método retorna la lista de facturas que se encuentran en
        estado "registrada" y que deberán ser recuperadas. El resultado
        está limitado a un máximo de 500 facturas. Las facturas deben
        ser procesadas para que entren el resto de facturas encoladas.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable. Si no se pasa valor
            retornará un listado de las facturas del RCF.
        """

        return self._llamar_metodo_soap("solicitarNuevasFacturas", oficina_contable)

    def descargar_factura(self, numero_registro: str):
        """Devuelve la respuesta del método SOAP `descargarFactura`.

        Este servicio permite descargar las facturas. Después de llamar
        a este servicio, y una vez comprobada la correcta recepción de
        la factura, el RCF debe llamar al servicio
        "confirmarDescargaFactura". El servicio de descarga de facturas,
        únicamente puede ser invocado para facturas en estado
        "Registrada". En otros casos el sistema generará un error.

        Parameters
        ----------
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe a descargar.
        """

        return self._llamar_metodo_soap("descargarFactura", numero_registro)

    def confirmar_descarga_factura(
        self, oficina_contable: str, numero_registro: str, codigo_rcf: str
    ):
        """Devuelve la respuesta del método SOAP `confirmarDescargaFactura`.

        Este servicio es el complementario al servicio descargar
        factura, es decir, el RCF deberá solicitar
        "confirmarDescargaFactura" para cada "descargarFactura" que se
        haya completado con éxito, de forma que la plataforma FACe pueda
        realizar todas las acciones relacionadas con la descarga de
        factura por parte del RCF.

        Este método actualiza la factura al estado 1300 automáticamente.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable.
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            consultarse su RCF.
        codigo_rcf : str
            Código del RCF a asignar a la factura.
        """

        return self._llamar_metodo_soap(
            "confirmarDescargaFactura", oficina_contable, numero_registro, codigo_rcf
        )

    def consultar_factura(self, numero_registro: str):
        """Devuelve la respuesta del método SOAP `consultarRegistro`.

        Este método permite consultar el estado de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            consultarse su estado.
        """

        return self._llamar_metodo_soap("consultarFactura", numero_registro)

    def consultar_listado_facturas(self, numeros_registro: list[str]):
        """Devuelve la respuesta del método SOAP `consultarListadoFacturas`.

        Este método permite consultar el estado de varias facturas. El
        servicio web limita a un máximo de 500 facturas la consulta.

        Parameters
        ----------
        numeros_registro : list[str]
            Números de registro en el REC, identificadores únicos de las
            facturas dentro de la plataforma FACe para las que quiere
            consultarse su estado.
        """

        return self._llamar_metodo_soap(
            "consultarListadoFacturas",
            numeros_registro,
            array_type="ns0:ArrayOfConsultarListadoFacturasRequest",
        )

    def cambiar_estado_factura(
        self, oficina_contable: str, numero_registro: str, codigo: str, comentario: str
    ):
        """Devuelve la respuesta del método SOAP `cambiarEstadoFactura`.

        Este método permite cambiar el estado de una factura.

        Este método permite cambiar el estado de una factura. Los
        estados 1300 y 3100 no están permitidos en este método, para
        ello deben usarse los métodos equivalentes a las peticiones SOAP
        `confirmarDescargaFactura` y `gestionarSolicitudAnulacion`
        respectivamente. El estado inicial 1200 tampoco es gestionable
        por este método.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            consultarse su RCF
        codigo : str
            Identificador del estado a asignar
        comentario : str
            Comentario asociado al cambio de estado de la factura
        """

        return self._llamar_metodo_soap(
            "cambiarEstadoFactura",
            oficina_contable,
            numero_registro,
            codigo,
            comentario,
        )

    def cambiar_estado_listado_facturas(
        self, facturas: list[PeticionCambiarEstadoFactura]
    ):
        """Devuelve la respuesta del método SOAP `cambiarEstadoListadoFacturas`.

        Este método permite el cambio de estado a múltiples facturas.

        Las restricciones de este método son iguales al método SOAP
        `cambiarEstadoFactura`. Se permite hasta un máximo de 100
        facturas en una misma llamada.

        Parameters
        ----------
        facturas : list[PeticionCambiarEstadoFactura]
            Lista de peticiones con los datos de las facturas a cambiar.
        """

        facturas_dict_list = []
        for factura in facturas:
            facturas_dict_list.append(
                {
                    "oficinaContable": factura.oficina_contable,
                    "numeroRegistro": factura.numero_registro,
                    "codigo": factura.codigo,
                    "comentario": factura.comentario,
                }
            )

        return self._llamar_metodo_soap(
            "cambiarEstadoListadoFacturas",
            facturas_dict_list,
            array_type="ns0:ArrayOfCambiarEstadoListadoFacturaRequest",
        )

    def consultar_codigo_rcf(self, numero_registro: str):
        """Devuelve la respuesta del método SOAP `consultarCodigoRCF`.

        Este método permite consultar el código RCF de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            consultarse su RCF.
        """

        return self._llamar_metodo_soap("consultarCodigoRCF", numero_registro)

    def cambiar_codigo_rcf(self, numero_registro: str, codigo_rcf: str):
        """Devuelve la respuesta del método SOAP `cambiarCodigoRCF`.

        Este método permite cambiar el código RCF de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            consultarse su RCF.
        codigo_rcf : str
            Código del RCF a asignar a la factura.
        """

        return self._llamar_metodo_soap("cambiarCodigoRCF", numero_registro, codigo_rcf)

    def solicitar_nuevas_anulaciones(self, oficina_contable: str):
        """Devuelve la respuesta del método SOAP `solicitarNuevasAnulaciones`.

        Este método retorna la lista de facturas que se encuentran en
        estado "solicitada anulación". El resultado está limitado a un
        máximo de 500 facturas. Las solicitudes deben ser procesadas
        para que entren el resto de solicitudes encoladas.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable. Si no se pasa valor
            retornará un listado de las facturas del RCF.
        """

        return self._llamar_metodo_soap("solicitarNuevasAnulaciones", oficina_contable)

    def gestionar_solicitud_anulacion_factura(
        self, oficina_contable: str, numero_registro: str, codigo: str, comentario: str
    ):
        """Devuelve la respuesta del método SOAP `gestionarSolicitudAnulacionFactura`.

        Este método permite gestionar una solicitud de anulación,
        aceptando o rechazando dicha solicitud.

        Parameters
        ----------
        oficina_contable : str
            Código DIR3 de la Oficina Contable
        numero_registro : str
            Número de registro, en el REC, de la factura para la que
            quiere gestionarse su solicitud de anulación
        codigo : str
            Identificador del estado a asignar
        comentario : str
            Comentario asociado a la gestión de la solicitud de
            anulación
        """

        return self._llamar_metodo_soap(
            "gestionarSolicitudAnulacionFactura",
            oficina_contable,
            numero_registro,
            codigo,
            comentario,
        )

    def gestionar_solicitud_anulacion_listado_facturas(
        self, facturas: list[PeticionSolicitudAnulacionListadoFactura]
    ):
        """Devuelve la respuesta del método SOAP `gestionarSolicitudAnulacionListadoFacturas`.

        Este método permite gestionar la solicitud de anulación de
        varias facturas.

        Se permite hasta un máximo de 100 facturas en una misma llamada.

        Parameters
        ----------
        facturas : list[PeticionSolicitudAnulacionListadoFactura]
            Lista de peticiones con los datos de las solicitudes de
            anulación a gestionar.
        """

        facturas_dict_list = []
        for factura in facturas:
            facturas_dict_list.append(
                {
                    "oficinaContable": factura.oficina_contable,
                    "numeroRegistro": factura.numero_registro,
                    "codigo": factura.codigo,
                    "comentarios": factura.comentario,
                }
            )

        return self._llamar_metodo_soap(
            "cambiarEstadoListadoFacturas",
            facturas_dict_list,
            array_type="ns0:ArrayOfGestionarSolicitudAnulacionListadoFacturasRequest",
        )

    def consultar_estado_cesion(self, numero_registro: str):
        """Devuelve la respuesta del método SOAP `consultarEstadoCesion`.

        Este método permite consultar el estado de la cesión de una factura.

        Parameters
        ----------
        numero_registro : str
            Número de registro, en el REC, de la factura para la que
            quiere consultarse el estado de la cesión.
        """

        return self._llamar_metodo_soap("consultarEstadoCesion", numero_registro)

    def obtener_documento_cesion(self, csv: str, repositorio: str, solicitante: dict):
        """Devuelve la respuesta del método SOAP `obtenerDocumentoCesion`.

        Este método permite obtener el documento de la cesión conectando al servicio de notarios.

        Parameters
        ----------
        csv : str
            Identificador del documento.
        repositorio : str
            Repositorio desde el que se obtiene el documento.
        solicitante : dict
            Datos del solicitante (nif, nombre, apellidos).
        """

        return self._llamar_metodo_soap(
            "obtenerDocumentoCesion", csv, repositorio, solicitante
        )

    def gestionar_cesion(self, numero_registro: str, codigo: str, comentario: str):
        """Devuelve la respuesta del método SOAP `gestionarCesion`.

        Este método permite gestionar una crédito, aceptando o
        rechazando dicha cesión.

        Parameters
        ----------
        numero_registro : str
            Número de registro, en el REC, de la factura para la que
            quiere gestionarse la cesión de crédito.
        codigo : str
            Identificador del estado a asignar
        comentario : str
            Comentario asociado a la gestión de la cesión de crédito.
        """

        return self._llamar_metodo_soap(
            "gestionarCesion",
            numero_registro,
            codigo,
            comentario,
        )

    def notifica_factura(
        self,
        numero_registro: str,
        fecha_registro: str,
        factura: str,
        organo_gestor: str,
        unidad_tramitadora: str,
        oficina_contable: str,
        codigo_rcf: str,
        estado: str,
    ):
        """Devuelve la respuesta del método SOAP `notificaFactura`.

        Este servicio permite notificar sobre una factura recibida en
        otro PGEFe. Se retorna un número de registro y fecha de registro
        para poder consultar y operar la factura en FACe.

        Parameters
        ----------
        numero_registro : str
            Número de registro del PGEFe.
        fecha_registro : str
            Fecha de registro del PGEFe formato en 'YYYY-MM-DDThh:mm:ss'
        factura : str
            Fichero factura en formato facturae 3.2 o 3.2.1 en base64
        organo_gestor : str
            Código DIR3 del Órgano Gestor.
        unidad_tramitadora : str
            Código DIR3 de la Unidad Tramitadora.
        oficina_contable : str
            Código DIR3 del Oficina Contable.
        codigo_rcf : str
            Código asignado dentro de RCF
        estado : str
            Código del estado de la factura
        """

        peticion = {
            "numeroRegistro": numero_registro,
            "fechaRegistro": fecha_registro,
            "factura": factura,
            "organoGestor": organo_gestor,
            "unidadTramitadora": unidad_tramitadora,
            "oficinaContable": oficina_contable,
            "codigoRCF": codigo_rcf,
            "estado": estado,
        }

        return self._llamar_metodo_soap("notificaFactura", peticion)

    def notifica_factura_no_electronica(
        self,
        numero_registro: str,
        fecha_registro: str,
        emisor: dict,
        receptor: dict,
        tercero: dict,
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
    ):
        """Simula una llamada al método `notificaFacturaNoElectronica` en FACe."""

        peticion = {
            "numeroRegistro": numero_registro,
            "fechaRegistro": fecha_registro,
            "emisor": emisor,
            "receptor": receptor,
            "tercero": tercero,
            "numero": numero,
            "serie": serie,
            "importe": importe,
            "fechaExpedicion": fecha_expedicion,
            "organoGestor": organo_gestor,
            "unidadTramitadora": unidad_tramitadora,
            "oficinaContable": oficina_contable,
            "codigoRCF": codigo_rcf,
            "estado": estado,
            "codCNAE": codigo_cnae,
        }

        return self._llamar_metodo_soap("notificaFacturaNoElectronica", peticion)
