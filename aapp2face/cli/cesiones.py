"""
Módulo para el comando `cesiones`
"""

import typer

from aapp2face import exceptions
from aapp2face.lib.objects import EstadoCesion

from .helpers import err_rprint, rprint

app = typer.Typer(help="Gestión de las cesiones de crédito.")


@app.command()
def consultar(
    ctx: typer.Context,
    numero_registro: str = typer.Argument(
        ...,
        show_default=False,
        help="Número de registro de la facturas a consultar.",
    ),
):
    """Consulta el estado de la cesión de una factura.

    Consulta el estado de la cesión de una factura cuyo identificador
    es facilitado.
    """

    try:
        cesion = ctx.obj.face_connection.consultar_estado_cesion(numero_registro)
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    if isinstance(cesion, EstadoCesion):
        rprint(f"[field]Número registro:[/field] [info]{cesion.numero_registro}[/info]")
        rprint(f"[field]Estado:[/field]          {cesion.codigo}")
        rprint(f"[field]Comentario:[/field]      {cesion.comentario}")
    else:
        rprint(f"[field]Número registro:[/field] [info]{cesion.id}[/info]")
        rprint(f"  [error]Error:[/error] {cesion.codigo} {cesion.descripcion}.")
