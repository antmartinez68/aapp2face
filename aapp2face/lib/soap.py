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
    """Clase de conexión a FACe usando SOAP"""

    def __init__(
        self, wsdl: str, cert: str, key: str, debug: bool = False, log_path: str = "."
    ):
        self._wsdl = wsdl
        self._cert = cert
        self._key = key
        self._debug = debug
        self._log_path = log_path
        self._connected = False

    def _connect(self) -> None:
        """Crea la conexión SOAP con FACe"""

        if not self._connected:
            try:
                self._history = HistoryPlugin()
                wsse = BinarySignatureTimestamp(self._key, self._cert)
                self._face = zeep.Client(self._wsdl, plugins=[self._history], wsse=wsse)
            except FileNotFoundError as e:
                ## Arregla esto. Tiene que generar su propia excepción
                print(e)
                exit(2)

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
            Código DIR3 de la Oficina Contable.
        numero_registro : str
            Número de registro en el REC, identificador único de la
            factura dentro de la plataforma FACe para la que quiere
            consultarse su RCF.
        codigo : str
            Identificador del código de estado a asignar.
        comentario : str
            Comentario asociado al cambio de estado de la factura.
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
        aceptándo o rechazando dicha solicitud.

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
