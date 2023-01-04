"""
Implementación de la interfaz FACeClient para conexiones reales
"""

import datetime
from pathlib import Path

import zeep
from lxml import etree
from zeep.plugins import HistoryPlugin

from .client import FACeClient
from .objects import FACeResult
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
