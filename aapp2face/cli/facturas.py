"""
Módulo para el comando `facturas`
"""

import dataclasses
from pathlib import Path
from typing import Optional

import typer

from aapp2face import exceptions
from aapp2face.lib.objects import (
    CambiarEstadoFactura,
    ConfirmaDescargaFactura,
    ConsultarFactura,
    NuevaFactura,
    PeticionCambiarEstadoFactura,
)

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


@app.command()
def descargar(
    ctx: typer.Context,
    force: Optional[bool] = typer.Option(
        False,
        "--force",
        "-f",
        help="Sobrescribe los archivos de factura o anexos si existen.",
    ),
    export: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        show_default=False,
        help="Exporta la salida a un archivo CSV.",
    ),
    numeros_registro: list[str] = typer.Argument(
        None,
        show_default=False,
        help="Números de registro de las facturas a descargar.",
    ),
):
    """Descarga facturas.

    Descarga las facturas correspondientes a los indentificadores
    facilitados. Si no se facilita ninguno se descargarán todas las
    facturas nuevas del RCF.

    En el directorio destino determinado por la configuración será
    creado un nuevo directorio por cada fatura usando como nombre el
    número de registro de esta y en él se descargarán tanto el archivo
    de la factura como los archivos de los correspondientes anexos si
    los tuviera.
    """

    verify_export(export)

    if not numeros_registro:
        facturas_nuevas = obtener_facturas_nuevas(ctx)
        numeros_registro = [factura.numero_registro for factura in facturas_nuevas]

    path = Path(ctx.obj.config["App"]["download_dir"])
    facturas = []
    for numero_registro in numeros_registro:
        try:
            # Descargar factura
            factura_en_proceso = ctx.obj.face_connection.descargar_factura(
                numero_registro
            )

            # Guardar factura
            path.joinpath(numero_registro).mkdir(parents=True, exist_ok=True)
            try:
                factura_en_proceso.guardar(path.joinpath(numero_registro), force)
            except FileExistsError:
                err_rprint(
                    f"[warning]Aviso:[/warning] El archivo [data]{factura_en_proceso.nombre}[/data] ya existe, no será sobrescrito.\n"
                )

            # Guardar anexos
            for anexo in factura_en_proceso.anexos:
                try:
                    anexo.guardar(path.joinpath(numero_registro), force)
                except FileExistsError:
                    err_rprint(
                        f"[warning]Aviso:[/warning] El archivo [data]{anexo.nombre}[/data] ya existe, no será sobrescrito.\n"
                    )

            # Añadir a lista de facturas descargas
            dict_factura = {}
            dict_factura["numero_registro"] = numero_registro
            dict_factura.update(dataclasses.asdict(factura_en_proceso))
            lista_anexos = [anexo["nombre"] for anexo in dict_factura["anexos"]]
            dict_factura["lista_anexos"] = ", ".join(lista_anexos)
            facturas.append(dict_factura)
        except exceptions.FACeManagementException as exc:
            err_rprint(
                f"[error]Error {exc.code}:[/error] {exc.msg} ([data]'{numero_registro}'[/data]).\n"
            )

    if export:
        export_data(facturas, export, ["factura", "mime", "anexos"])
    else:
        for factura in facturas:
            rprint(
                f"[field]Núm. Registro:[/field] [info]{factura['numero_registro']}[/info]"
            )
            rprint(f"[field]Núm. Factura:[/field]  {factura['numero']}")
            rprint(f"[field]Serie:[/field]         {factura['serie']}")
            rprint(f"[field]Importe:[/field]       {factura['importe']}")
            rprint(f"[field]Proveedor:[/field]     {factura['proveedor']}")
            rprint(f"[field]Archivo:[/field]       {factura['nombre']}")
            rprint(f"[field]Anexos:[/field]        {factura['lista_anexos']}\n")

    rprint(f"[info]{len(facturas)}[/info] facturas descargadas")


@app.command()
def confirmar(
    ctx: typer.Context,
    oficina_contable: str = typer.Argument(
        ...,
        show_default=False,
        help="Código DIR3 de la Oficina Contable.",
    ),
    numero_registro: str = typer.Argument(
        ...,
        show_default=False,
        help="Número de registro de la factura a confirmar.",
    ),
    codigo_rcf: str = typer.Argument(
        ...,
        show_default=False,
        help="Código RCF que se asignará a la factura.",
    ),
):
    """Confirma la descarga de una factura.

    Tras la descarga de una factura debe utilizarse este comando para
    confirmar que el proceso de descarga se ha realizado con éxito, de
    forma que la plataforma FACe pueda realizar todas las acciones
    relacionadas con la descarga de la factura por parte del RCF.

    Tras confirmar la descarga de una factura, su estado queda
    actualizado automáticamente a 1300.
    """

    try:
        confirmacion: ConfirmaDescargaFactura = (
            ctx.obj.face_connection.confirmar_descarga_factura(
                oficina_contable, numero_registro, codigo_rcf
            )
        )
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    rprint(f"[field]Oficina contable:[/field]   {confirmacion.oficina_contable}")
    rprint(f"[field]Número de registro:[/field] {confirmacion.numero_registro}")
    rprint(f"[field]Código de estado:[/field]   {confirmacion.codigo}")


@app.command()
def consultar(
    ctx: typer.Context,
    export: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        show_default=False,
        help="Exporta la salida a un archivo CSV.",
    ),
    numeros_registro: list[str] = typer.Argument(
        ...,
        show_default=False,
        help="Números de registro de las facturas a consultar.",
    ),
):
    """Consulta el estado de facturas.

    Consulta el estado de las facturas cuyos identificadores son
    facilitados.
    """

    try:
        facturas = ctx.obj.face_connection.consultar_listado_facturas(numeros_registro)
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    for factura in facturas:
        if isinstance(factura, ConsultarFactura):
            rprint(
                f"[field]Número registro:[/field] [info]{factura.numero_registro}[/info]"
            )
            rprint(f"[field]Tramitación:[/field]")
            rprint(f"[field]  Código:[/field]        {factura.tramitacion.codigo}")
            rprint(f"[field]  Descripción:[/field]   {factura.tramitacion.descripcion}")
            rprint(f"[field]  Motivo:[/field]        {factura.tramitacion.motivo}")
            rprint(f"[field]Anulación:[/field]")
            rprint(f"[field]  Código:[/field]        {factura.anulacion.codigo}")
            rprint(f"[field]  Descripción:[/field]   {factura.anulacion.descripcion}")
            rprint(f"[field]  Motivo:[/field]        {factura.anulacion.motivo}")
        else:
            rprint(f"[field]Número registro:[/field] [info]{factura.id}[/info]")
            rprint(f"  [error]Error:[/error] {factura.codigo} {factura.descripcion}.")
        print()


@app.command()
def estado(
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
        help="Números de registro de las facturas a cambiar estado.",
    ),
):
    """Cambia el estado de las facturas.

    Si se indican varias facturas, todas ellas deben pertenecer a la
    misma Oficina Contable. El nuevo estado y comentario facilitados
    serán asignados a todas las facturas indicadas. Obsérvese que el
    parámetro comentario es obligatorio. Si se desea dejar en blanco se
    de indicar explícitamente, por ejemplo, usando comillas ("").

    Los estados 1300 y 3100 no pueden ser asignados mediante este
    comando ya que estos estados son asignados de forma automática al
    realizar las operaciones de confirmación de descarga de una factura
    y gestión de la solicitud de anulación respectivamente. El estado
    inicial 1200 tampoco es gestionable mediante este comando.
    """

    peticiones: list[PeticionCambiarEstadoFactura] = []
    for numero_registro in numeros_registro:
        peticion = PeticionCambiarEstadoFactura(
            oficina_contable, numero_registro, codigo, comentario
        )
        peticiones.append(peticion)

    try:
        confirmaciones: CambiarEstadoFactura = (
            ctx.obj.face_connection.cambiar_estado_listado_facturas(peticiones)
        )
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    errors = 0
    for confirmacion in confirmaciones:
        if isinstance(confirmacion, CambiarEstadoFactura):
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


@app.command()
def rcf(
    ctx: typer.Context,
    numero_registro: str = typer.Argument(
        ...,
        show_default=False,
        help="Número de registro de la facturas a consultar.",
    ),
):
    """Consulta el código RCF de una factura.

    Consulta el código RCF asignado a una factura cuyo indentificador es
    facilitado.
    """

    try:
        rcf = ctx.obj.face_connection.consultar_codigo_rcf(numero_registro)
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    if rcf == "":
        rprint("Factura sin código RCF")
    else:
        rprint(f"[field]Código RCF:[/field] {rcf}")


@app.command()
def crcf(
    ctx: typer.Context,
    numero_registro: str = typer.Argument(
        ...,
        show_default=False,
        help="Número de registro de la factura a actualizar.",
    ),
    codigo_rcf: str = typer.Argument(
        ...,
        show_default=False,
        help="Código RCF que se asignará a la factura.",
    ),
):
    """Cambia el código RCF asginado a una factura.

    Asigna el código RCF facilitado a la factura con el número de
    registro indicado.
    """

    try:
        rcf = ctx.obj.face_connection.cambiar_codigo_rcf(numero_registro, codigo_rcf)
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    rprint(f"[field]Código RCF:[/field] {rcf}")
