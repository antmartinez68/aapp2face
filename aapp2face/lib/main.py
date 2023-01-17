"""
Módulo principal de la librería AAPP2FACe
"""

from .client import FACeClient
from .objects import Estado, NuevaFactura, Relacion, UnidadDir3


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
