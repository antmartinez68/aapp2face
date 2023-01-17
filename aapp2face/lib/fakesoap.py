"""
Implementación de la interfaz FACeClient para conexiones simuladas
"""

import json
from pathlib import Path

from . import exceptions
from .client import FACeClient
from .objects import FACeResult

FILE_RESPONSE_EXTENSION = "json"


class FACeFakeSoapClient(FACeClient):
    """Clase que simula respuestas de una conexión a FACe a partir de
    archivos preconfigurados
    """

    def __init__(self, responses_path: Path):
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
