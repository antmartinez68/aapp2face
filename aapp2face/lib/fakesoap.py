"""
Implementación de la interfaz FACeClient para conexiones simuladas
"""

import json
from pathlib import Path

from . import exceptions
from .client import FACeClient
from .objects import (
    FACeResult,
    PeticionCambiarEstadoFactura,
    PeticionSolicitudAnulacionListadoFactura,
)

FILE_RESPONSE_EXTENSION = "json"


class FACeFakeSoapClient(FACeClient):
    """Clase del conector FACe para simulación a partir de archivos preconfigurados."""

    def __init__(self, responses_path: Path):
        """Constructor

        Parameters
        ----------
        responses_path : Path
            Ruta de los archivos respuesta preconfigurados
        """

        super().__init__()
        self._responses_path = responses_path
        self._set_suffix = f".{FILE_RESPONSE_EXTENSION}"

    def _import_response(self, filename_prefix: str) -> dict:
        """Importa un archivo preconfigurado que simula respuesta FACe

        Parameters
        ----------
        filename_prefix : str
            Prefijo del archivo a importar. Normalmente será el nombre del
            método FACe a simular seguido de los parámetros separados por
            puntos.

        Raises
        ------
        FACeManagementException
            Si el archivo a importar no existe.
        """

        file = Path(self._responses_path).joinpath(filename_prefix + self._set_suffix)

        if not file.exists():
            raise exceptions.FACeManagementException(
                "555",
                f"No existe archivo con respuesta para simular la petición ([data]'{filename_prefix + self._set_suffix}'[/data])",
            )

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        result_header = FACeResult(
            data["resultado"]["codigo"],
            data["resultado"]["descripcion"],
            data["resultado"]["codigoSeguimiento"],
        )

        self._verify_result_header(result_header)

        return data

    def consultar_estados(self):
        """Simula una llamada al método `consultarEstados` en FACe."""

        return self._import_response("consultarEstados")

    def consultar_unidades(self):
        """Simula una llamada al método `consultarUnidades` en FACe."""

        return self._import_response("consultarUnidades")

    def solicitar_nuevas_facturas(self, oficina_contable: str):
        """Simula una llamada al método `consultarFactura` en FACe."""

        if oficina_contable == "":
            filename_prefix = "solicitarNuevasFacturas"
        else:
            filename_prefix = f"solicitarNuevasFacturas.{oficina_contable}"

        return self._import_response(filename_prefix)

    def descargar_factura(self, numero_registro: str):
        """Simula una llamada al método `descargarFactura` en FACe."""

        return self._import_response(f"descargarFactura.{numero_registro}")

    def confirmar_descarga_factura(
        self, oficina_contable: str, numero_registro: str, codigo_rcf: str
    ):
        """Simula una llamada al método `confirmarDescargaFactura` en FACe."""

        return self._import_response(
            f"confirmarDescargaFactura.{oficina_contable}.{numero_registro}"
        )

    def consultar_factura(self, numero_registro: str):
        """Simula una llamada al método `consultarFactura` en FACe."""

        return self._import_response(f"consultarListadoFacturas.{numero_registro}")

    def consultar_listado_facturas(self, numeros_registro: list[str]):
        """Simula una llamada al método `consultarListadoFacturas` en FACe."""

        str_numeros_registro = ".".join(numeros_registro)

        return self._import_response(f"consultarListadoFacturas.{str_numeros_registro}")

    def cambiar_estado_factura(
        self, oficina_contable: str, numero_registro: str, codigo: str, comentario: str
    ):
        """Simula una llamada al método `cambiarEstadoFactura` en FACe."""

        result = self._import_response(
            f"cambiarEstadoFactura.{oficina_contable}.{numero_registro}"
        )

        # Simulación de algunos de los códigos de estado que provocan error
        estados_permitidos = (
            "1200",
            "1300",
            "1400",
            "2100",
            "2300",
            "2400",
            "2500",
            "2600",
            "3100",
            "4100",
            "4200",
            "4300",
            "4400",
        )

        if codigo not in estados_permitidos:
            raise exceptions.FACeManagementException(
                "405",
                f"No existe el código de estado {codigo}",
            )

        if codigo == "1200" or codigo == "3100":
            raise exceptions.FACeManagementException(
                "505",
                "Esta transición no esta permitida a través de este web service",
            )

        result["factura"]["codigo"] = codigo

        return result

    def cambiar_estado_listado_facturas(
        self, facturas: list[PeticionCambiarEstadoFactura]
    ):
        """Simula una llamada al método `cambiarEstadoListadoFacturas` en FACe."""

        # Este método falsea el que debería ser su comportamiento para
        # permitir probar de forma rápida el cambio de estado desde CLI.
        oficina_contable = facturas[0].oficina_contable
        codigo_estado = facturas[0].codigo
        numeros_registro = [peticion.numero_registro for peticion in facturas]
        str_numeros_registro = ".".join(numeros_registro)

        result = self._import_response(
            f"cambiarEstadoListadoFacturas.{oficina_contable}.{str_numeros_registro}"
        )

        for factura in result["facturas"]["cambiarEstadoListadoFacturas"]:
            if factura["codigo"] == "0":
                factura["factura"]["codigo"] = codigo_estado

        return result

    def consultar_codigo_rcf(self, numero_registro: str):
        """Simula una llamada al método `consultarCodigoRCF` en FACe."""

        return self._import_response(f"consultarCodigoRCF.{numero_registro}")

    def cambiar_codigo_rcf(self, numero_registro: str, codigo_rcf: str):
        """Simula una llamada al método `cambiarCodigoRCF` en FACe."""

        result = self._import_response(f"cambiarCodigoRCF.{numero_registro}")
        result["codigoRCF"] = codigo_rcf

        return result

    def solicitar_nuevas_anulaciones(self, oficina_contable: str):
        """Simula una llamada al método `solicitarNuevasAnulaciones` en FACe."""

        if oficina_contable == "":
            filename_prefix = "solicitarNuevasAnulaciones"
        else:
            filename_prefix = f"solicitarNuevasAnulaciones.{oficina_contable}"

        return self._import_response(filename_prefix)

    def gestionar_solicitud_anulacion_factura(
        self, oficina_contable: str, numero_registro: str, codigo: str, comentario: str
    ):
        """Simula una llamada al método `gestionarSolicitudAnulacionFactura` en FACe."""

        result = self._import_response(
            f"gestionarSolicitudAnulacionFactura.{oficina_contable}.{numero_registro}"
        )

        # Simulación de algunos de los códigos de estado que provocan error
        estados_permitidos = (
            "1200",
            "1300",
            "1400",
            "2100",
            "2300",
            "2400",
            "2500",
            "2600",
            "3100",
            "4100",
            "4200",
            "4300",
            "4400",
        )

        if codigo not in estados_permitidos:
            raise exceptions.FACeManagementException(
                "405",
                f"No existe el código de estado {codigo}",
            )

        if codigo == "1200" or codigo == "3100":
            raise exceptions.FACeManagementException(
                "505",
                "Esta transición no esta permitida a través de este web service",
            )

        result["factura"]["codigo"] = codigo

        return result

    def gestionar_solicitud_anulacion_listado_facturas(
        self, facturas: list[PeticionSolicitudAnulacionListadoFactura]
    ):
        """Simula una llamada al método `gestionarSolicitudAnulacionFacturas` en FACe."""

        # Este método falsea el que debería ser su comportamiento para
        # permitir probar de forma rápida el cambio de estado desde CLI.
        oficina_contable = facturas[0].oficina_contable
        codigo_estado = facturas[0].codigo
        numeros_registro = [peticion.numero_registro for peticion in facturas]
        str_numeros_registro = ".".join(numeros_registro)

        result = self._import_response(
            f"gestionarSolicitudAnulacionListadoFacturas.{oficina_contable}.{str_numeros_registro}"
        )

        for factura in result["facturas"]["gestionarSolicitudAnulacionListadoFacturas"]:
            if factura["codigo"] == "0":
                factura["factura"]["codigo"] = codigo_estado

        return result

    def consultar_estado_cesion(self, numero_registro: str):
        """Simula una llamada al método `consultarEstadoCesion` en FACe."""

        return self._import_response(f"consultarEstadoCesion.{numero_registro}")

    def obtener_documento_cesion(self, csv: str, repositorio: str, solicitante: dict):
        """Simula una llamada al método `obtenerDocumentoCesion`en FACe."""

        return self._import_response(
            f"obtenerDocumentoCesion.{csv}.{repositorio}."
            f"{solicitante['nif']}.{solicitante['nombre']}.{solicitante['apellidos']}"
        )

    def gestionar_cesion(self, numero_registro: str, codigo: str, comentario: str):
        """Simula una llamada al método `gestionarCesion` en FACe."""

        result = self._import_response(f"gestionarCesion.{numero_registro}")

        # Simulación de algunos de los códigos de estado que provocan error
        estados_permitidos = (
            "1200",
            "1300",
            "1400",
            "2100",
            "2300",
            "2400",
            "2500",
            "2600",
            "3100",
            "4100",
            "4200",
            "4300",
            "6100",
            "6200",
            "6300",
        )

        if codigo not in estados_permitidos:
            raise exceptions.FACeManagementException(
                "405",
                f"No existe el código de estado {codigo}",
            )

        if codigo != "6200" and codigo != "6300":
            raise exceptions.FACeManagementException(
                "505",
                "Esta transición no esta permitida a través de este web service",
            )

        result["cesion"]["codigo"] = codigo
        result["cesion"]["comentario"] = comentario

        return result

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
        """Simula una llamada al método `notificaFactura` en FACe."""

        return self._import_response(f"notificaFactura.{numero_registro}")

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

        return self._import_response(f"notificaFacturaNoElectronica.{numero_registro}")
