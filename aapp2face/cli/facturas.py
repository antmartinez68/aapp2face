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
