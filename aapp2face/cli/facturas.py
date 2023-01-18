"""
Módulo para el comando `facturas`
"""

import dataclasses
from pathlib import Path
from typing import Optional

import typer

from aapp2face import exceptions
from aapp2face.lib.objects import NuevaFactura

from .helpers import err_rprint, export_data, rprint, verify_export

app = typer.Typer(help="Gestión de facturas.")


def obtener_facturas_nuevas(
    ctx: typer.Context, oficina_contable: str = ""
) -> list[NuevaFactura]:
    """Devuelve las facturas nuevas registradas en FACe.

    Parameters
    ----------
    ctx : typer.Context
        Contexto que contiene la conexión a FACe
    oficina_contable : str, optional
        Código DIR3 de la Oficina Contable. Si no se pasa valor
        retornará un listado de las facturas del RCF.
    """

    try:
        facturas = ctx.obj.face_connection.solicitar_nuevas_facturas(oficina_contable)
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(1)

    return facturas


@app.command()
def nuevas(
    ctx: typer.Context,
    export: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        show_default=False,
        help="Exporta la salida a un archivo CSV.",
    ),
    oficina_contable: Optional[str] = typer.Argument(
        "", help="Código DIR3 de la Oficina Contable."
    ),
):
    """Devuelve las nuevas facturas registradas en FACe.

    Consulta las facturas que se encuentran en el estado "registrada".
    Periódicamente se deberá utilizar este comando para obtener las
    facturas que posteriormente deberán ser recuperadas.

    El resultado está limitado por el servicio de FACe a un máximo de
    500 facturas. Se deben procesar las facturas para que entren el
    resto de facturas encoladas.
    """

    verify_export(export)

    facturas = obtener_facturas_nuevas(ctx, oficina_contable)

    if export:
        data = [dataclasses.asdict(factura) for factura in facturas]
        export_data(data, export)
    else:
        for factura in facturas:
            rprint(
                f"[field]Número registro:[/field]    [info]{factura.numero_registro}[/info]"
            )
            rprint(f"[field]Fecha registro:[/field]     {factura.fecha_hora_registro}")
            rprint(f"[field]Oficina contable:[/field]   {factura.oficina_contable}")
            rprint(f"[field]Órgano gestor:[/field]      {factura.organo_gestor}")
            rprint(f"[field]Unidad tramitadora:[/field] {factura.unidad_tramitadora}\n")

    rprint(f"[info]{len(facturas)}[/info] nuevas facturas disponibles")
