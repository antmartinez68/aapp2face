"""
Módulo para el comando `anulaciones`
"""

import dataclasses
from pathlib import Path
from typing import Optional

import typer

from aapp2face import exceptions

from .helpers import err_rprint, export_data, rprint, verify_export

app = typer.Typer(help="Gestión de solicitudes de anulación.")


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
    """Devuelve las facturas que se encuentran en estado "solicitada anulación".

    Si no se pasa el código de la Oficina Contable, retornará todas las
    facturas en este estado del RCF.

    El RCF deberá solicitar periódicamente este servicio para conocer
    las solicitudes de anulación de facturas recibidas en FACe por parte
    de los proveedores.

    El resultado está limitado a un máximo de 500 facturas. Las
    solicitudes deben ser procesadas para que entren el resto de
    solicitudes encoladas.
    """

    verify_export(export)

    try:
        facturas = ctx.obj.face_connection.solicitar_nuevas_anulaciones(
            oficina_contable
        )
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    if export:
        data = [dataclasses.asdict(factura) for factura in facturas]
        export_data(data, export)
    else:
        for factura in facturas:
            rprint(
                f"[field]Número registro:[/field]    [info]{factura.numero_registro}[/info]"
            )
            rprint(f"[field]Fecha solicitud:[/field]    {factura.fecha_hora_solicitud}")
            rprint(f"[field]Oficina contable:[/field]   {factura.oficina_contable}")
            rprint(f"[field]Órgano gestor:[/field]      {factura.organo_gestor}")
            rprint(f"[field]Unidad tramitadora:[/field] {factura.unidad_tramitadora}")
            rprint(f"[field]Motivo:[/field]             {factura.motivo}")
            print("")

    rprint(f"[info]{len(facturas)}[/info] nuevas solicitudes de anulación")
