"""
Módulo para el comando `cesiones`
"""

from pathlib import Path
from typing import Optional

import typer

from aapp2face import exceptions
from aapp2face.lib.objects import DatosSolicitante, EstadoCesion, GestionarCesion

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

    rprint(f"[field]Número registro:[/field] [info]{cesion.numero_registro}[/info]")
    rprint(f"[field]Estado:[/field]          {cesion.codigo}")
    rprint(f"[field]Comentario:[/field]      {cesion.comentario}")


@app.command()
def documento(
    ctx: typer.Context,
    force: Optional[bool] = typer.Option(
        False,
        "--force",
        "-f",
        help="Sobrescribe los archivos de factura o anexos si existen.",
    ),
    csv: str = typer.Argument(
        ...,
        show_default=False,
        help="CSV del documento a obtener.",
    ),
    repositorio: str = typer.Argument(
        ...,
        show_default=False,
        help="Repositorio desde el que se obtiene el documento.",
    ),
    nif: str = typer.Argument(
        ...,
        show_default=False,
        help="NIF del solicitante.",
    ),
    nombre: str = typer.Argument(
        ...,
        show_default=False,
        help="Nombre del solicitante.",
    ),
    apellidos: str = typer.Argument(
        ...,
        show_default=False,
        help="Apellidos del solicitante.",
    ),
):
    """Obtiene el documento de la cesión.

    Obtiene el documento de la cesión conectando al servicio de notarios.
    """

    try:
        documento = ctx.obj.face_connection.obtener_documento_cesion(
            csv, repositorio, DatosSolicitante(nif, nombre, apellidos)
        )
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    # Guardar documento
    path = Path(ctx.obj.config["App"]["download_dir"])
    path.mkdir(parents=True, exist_ok=True)
    try:
        documento.guardar(path, force)
    except FileExistsError:
        err_rprint(
            f"[warning]Aviso:[/warning] El archivo [data]{documento.nombre}[/data] ya existe, no será sobrescrito."
        )

    rprint(f"[field]Núm. Registro:[/field] [info]{documento.numero_registro}[/info]")
    rprint(f"[field]Archivo:[/field]       {documento.nombre}")
    rprint(f"[field]Mime:[/field]          {documento.mime}")


@app.command()
def gestionar(
    ctx: typer.Context,
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
    numero_registro: str = typer.Argument(
        ...,
        show_default=False,
        help="Números de registro de la factura de la cesión.",
    ),
):
    """Gestiona la cesión de crédito de una factura.

    Obsérvese que el parámetro comentario es obligatorio. Si se desea
    dejar en blanco se de indicar explícitamente, por ejemplo, usando
    comillas ("").
    """

    try:
        cesion: GestionarCesion = ctx.obj.face_connection.gestionar_cesion(
            numero_registro, codigo, comentario
        )
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    rprint(f"[field]Número de registro:[/field] [info]{cesion.numero_registro}[/info]")
    rprint(f"[field]Código de estado:[/field]   {cesion.codigo}")
    rprint(f"[field]Comentario:[/field]         {cesion.comentario}")
