"""
Módulo para el comando `anulaciones`
"""

import dataclasses
from pathlib import Path
from typing import Optional

import typer

from aapp2face import exceptions
from aapp2face.lib.objects import (
    GestionarSolicitudAnulacionFactura,
    PeticionSolicitudAnulacionListadoFactura,
)

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


@app.command()
def gestionar(
    ctx: typer.Context,
    oficina_contable: str = typer.Argument(
        ...,
        show_default=False,
        help="Código DIR3 de la Oficina Contable.",
    ),
    codigo: str = typer.Argument(
        ...,
        show_default=False,
        help="Identificador del código de estado a asignar.",
    ),
    comentario: str = typer.Argument(
        ...,
        show_default=False,
        help="Comentario asociado al cambio de estado.",
    ),
    numeros_registro: list[str] = typer.Argument(
        ...,
        show_default=False,
        help="Números de registro de las facturas con solicitud de anulación.",
    ),
):
    """Gestiona las solicitudes de anulación de facturas.

    Si se indican varias facturas, todas ellas deben pertenecer a la
    misma Oficina Contable. El nuevo estado y comentario facilitados
    serán asignados a todas las facturas indicadas. Obsérvese que el
    parámetro comentario es obligatorio. Si se desea dejar en blanco se
    de indicar explícitamente, por ejemplo, usando comillas ("").
    """

    peticiones: list[PeticionSolicitudAnulacionListadoFactura] = []
    for numero_registro in numeros_registro:
        peticion = PeticionSolicitudAnulacionListadoFactura(
            oficina_contable, numero_registro, codigo, comentario
        )
        peticiones.append(peticion)

    try:
        confirmaciones: GestionarSolicitudAnulacionFactura = (
            ctx.obj.face_connection.gestionar_solicitud_anulacion_listado_facturas(
                peticiones
            )
        )
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    errors = 0
    for confirmacion in confirmaciones:
        if isinstance(confirmacion, GestionarSolicitudAnulacionFactura):
            rprint(
                f"[field]Número de registro:[/field] [info]{confirmacion.numero_registro}[/info]"
            )
            rprint(f"[field]Código de estado:[/field]   {confirmacion.codigo}")
        else:
            rprint(f"[field]Número de registro:[/field] [info]{confirmacion.id}[/info]")
            rprint(
                f"  [error]Error:[/error] {confirmacion.codigo} {confirmacion.descripcion}."
            )
            errors += 1
        print()
    rprint(
        f"[info]{len(confirmaciones)-errors}[/info] cambios correctos y [error]{errors}[/error] errores."
    )
