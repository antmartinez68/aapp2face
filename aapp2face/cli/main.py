"""
Módulo CLI de AAPP2FACe
"""

import dataclasses
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

import typer

from aapp2face import (
    FACeConnection,
    FACeFakeSoapClient,
    FACeSoapClient,
    __version__,
    exceptions,
)

from . import anulaciones, cesiones, facturas
from .helpers import err_rprint, export_data, get_config_path, rprint, verify_export

# Config constants
CONFIG_FILENAME = "config.ini"
FACE_URL_PROD = "https://webservice.face.gob.es/facturasrcf2?wsdl"
FACE_URL_STAGING = "https://se-face-webservice.redsara.es/facturasrcf2?wsdl"
USE_STAGING = True
CERT_FILENAME = "./cert.pem"
KEY_FILENAME = "./key.pem"
DOWNLOAD_DIR = "./descargas"
DEBUG_ENABLED = True
DEBUG_LOG_DIR = "."
FAKE_RESPONSES_DIR = "."

app = typer.Typer(no_args_is_help=True)
app.add_typer(facturas.app, name="facturas")
app.add_typer(anulaciones.app, name="anulaciones")
app.add_typer(cesiones.app, name="cesiones")


class AppData:
    """Clase del objeto especial interno que contiene información
    relevante usada a nivel global.
    """

    def __init__(
        self,
        config_file: Path,
        config: ConfigParser,
        face_connection: FACeConnection,
    ):
        self.face_connection = face_connection
        self.config_file = config_file
        self.config = config


def get_default_config() -> ConfigParser:
    """Devuelve un objeto que contiene la configuración por defecto."""

    config = ConfigParser()
    config["FACe"] = {}
    config["FACe"]["url_prod"] = FACE_URL_PROD
    config["FACe"]["url_staging"] = FACE_URL_STAGING
    config["FACe"]["use_staging"] = str(USE_STAGING)
    config["X509"] = {}
    config["X509"]["cert_file"] = CERT_FILENAME
    config["X509"]["key_file"] = KEY_FILENAME
    config["App"] = {}
    config["App"]["download_dir"] = DOWNLOAD_DIR
    config["Debug"] = {}
    config["Debug"]["enabled"] = str(DEBUG_ENABLED)
    config["Debug"]["log_dir"] = DEBUG_LOG_DIR
    config["Fake"] = {}
    config["Fake"]["responses_dir"] = FAKE_RESPONSES_DIR

    return config


@app.command()
def init(ctx: typer.Context):
    """Genera un archivo de configuración nuevo mediante asistente."""

    if ctx.obj.config_file.exists():
        if not typer.confirm(
            "Ya existe el archivo de configuración. ¿Desea sobreescribirlo?"
        ):
            raise typer.Abort()
    else:
        ctx.obj.config_file.parent.mkdir(parents=True, exist_ok=True)

    config = get_default_config()

    config["FACe"]["url_prod"] = typer.prompt(
        "URL Producción FACe", config["FACe"]["url_prod"]
    )
    config["FACe"]["url_staging"] = typer.prompt(
        "URL Staging FACe", config["FACe"]["url_staging"]
    )
    config["FACe"]["use_staging"] = typer.confirm(
        "¿Usar entorno de pruebas por defecto?", config["FACe"]["use_staging"]
    )
    config["X509"]["cert_file"] = typer.prompt(
        "Archivo con el certificado de firma", config["X509"]["cert_file"]
    )
    config["X509"]["key_file"] = typer.prompt(
        "Archivo con la clave privada del certificado", config["X509"]["key_file"]
    )
    config["App"]["download_dir"] = typer.prompt(
        "Directorio descarga facturas", config["App"]["download_dir"]
    )

    with open(ctx.obj.config_file, "w") as file:
        config.write(file)

    rprint("[green]Archivo de configuración generado!![/green]")


@app.command()
def config(ctx: typer.Context):
    """Muestra los valores de configuración que están siendo aplicados."""

    for seccion in ctx.obj.config.sections():
        for opcion in ctx.obj.config.options(seccion):
            valor = ctx.obj.config.get(seccion, opcion)
            rprint(f"[blue]{seccion}.{opcion}[/blue] = {valor}")


@app.command()
def estados(
    ctx: typer.Context,
    export: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        show_default=False,
        help="Exporta la salida a un archivo CSV.",
    ),
):
    """Lista los estados que maneja FACe para la gestión de las facturas.

    Existen dos flujos principales, el ordinario y el de anulación. El
    flujo ordinario corresponde al ciclo de vida de la factura, y el
    flujo de anulación corresponde al ciclo de solicitud de anulación.
    """

    verify_export(export)

    try:
        estados = ctx.obj.face_connection.consultar_estados()
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    if export:
        data = [dataclasses.asdict(estado) for estado in estados]
        export_data(data, export)
    else:
        for estado in estados:
            rprint(f"[field]Código:[/field]         [info]{estado.codigo}[/info]")
            rprint(f"[field]Flujo:[/field]          {estado.flujo}")
            rprint(f"[field]Nombre:[/field]         {estado.nombre}")
            rprint(f"[field]Nombre público:[/field] {estado.nombre_publico}")
            rprint(f"[field]Descripción:[/field]    {estado.descripcion}")
            print("")

    rprint(f"[info]{len(estados)}[/info] estados disponibles")


@app.command()
def unidades(
    ctx: typer.Context,
    export: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        show_default=False,
        help="Exporta la salida a un archivo CSV.",
    ),
):
    """Lista las relaciones OG-UT-OC asociadas al RCF.

    Las relaciones OG-UT-OC obtenidas son las asociadas al RCF que firma
    la petición.
    """

    verify_export(export)

    try:
        relaciones = ctx.obj.face_connection.consultar_unidades()
    except exceptions.FACeManagementException as exc:
        err_rprint(f"[error]Error {exc.code}:[/error] {exc.msg}.")
        raise typer.Exit(4)

    if export:
        data = []
        for relacion in relaciones:
            dict_relacion = {
                "organo_gestor_codigo": relacion.organo_gestor.codigo,
                "organo_gestor_nombre": relacion.organo_gestor.nombre,
                "unidad_tramitadora_codigo": relacion.unidad_tramitadora.codigo,
                "unidad_tramitadora_nombre": relacion.unidad_tramitadora.nombre,
                "oficina_contable_codigo": relacion.oficina_contable.codigo,
                "oficina_contable_nombre": relacion.oficina_contable.nombre,
            }
            data.append(dict_relacion)
        export_data(data, export)
    else:
        for relacion in relaciones:
            rprint(f"[field]Órgano gestor:[/field]")
            rprint(f"  [field]Código:[/field] {relacion.organo_gestor.codigo}")
            rprint(f"  [field]Nombre:[/field] {relacion.organo_gestor.nombre}")

            rprint(f"[field]Unidad tramitadora:[/field]")
            rprint(f"  [field]Código:[/field] {relacion.unidad_tramitadora.codigo}")
            rprint(f"  [field]Nombre:[/field] {relacion.unidad_tramitadora.nombre}")

            rprint(f"[field]Oficina contable:[/field]")
            rprint(f"  [field]Código:[/field] {relacion.oficina_contable.codigo}")
            rprint(f"  [field]Nombre:[/field] {relacion.oficina_contable.nombre}")
            print("")

    rprint(
        f"[info]{len(relaciones)}[/info] relaciones {'exportadas' if export else 'disponibles'}"
    )


def version_callback(value: bool):
    """Callback de mostrado de la versión"""

    if value:
        print(f"AAPP2FACe CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        envvar="AAPP2FACE_CONFIG",
        show_envvar=False,
        show_default=False,
        help="Permite indicar un archivo de configuración alternativo.",
    ),
    fake: Optional[bool] = typer.Option(
        None,
        "--fake",
        "-f",
        show_default=False,
        help="Obtiene datos desde archivo de prueba en lugar de conectar con FACe.",
        hidden=True,
    ),
    fake_set: Optional[str] = typer.Option(
        None,
        "--fake-set",
        envvar="AAPP2FACE_FAKE_RESPONSES_DIR",
        show_envvar=False,
        show_default=False,
        help="Ruta donde se ubican las respuestas de prueba del modo simulación.",
        exists=True,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        hidden=True,
    ),
    url_prod: Optional[str] = typer.Option(
        None,
        envvar="AAPP2FACE_URL_PROD",
        show_envvar=False,
        show_default=False,
        help="URL de ubicación del WSDL para el entorno de producción de FACe.",
    ),
    url_staging: Optional[str] = typer.Option(
        None,
        envvar="AAPP2FACE_URL_STAGING",
        show_envvar=False,
        show_default=False,
        help="URL de ubicación del WSDL para el entorno de pruebas de FACe.",
    ),
    use_staging: Optional[bool] = typer.Option(
        None,
        "--use-staging/--use-prod",
        "-u/-U",
        envvar="AAPP2FACE_USE_STAGING",
        show_envvar=False,
        show_default=False,
        help="Fuerza el uso del entorno de pruebas en la peticiones a FACe.",
    ),
    cert_file: Optional[Path] = typer.Option(
        None,
        envvar="AAPP2FACE_CERT_FILE",
        show_envvar=False,
        show_default=False,
        help="Archivo que contiene el certificado para firma peticiones.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    key_file: Optional[Path] = typer.Option(
        None,
        envvar="AAPP2FACE_KEY_FILE",
        show_envvar=False,
        show_default=False,
        help="Archivo que contiene la clave privada del certificado.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    download_dir: Optional[Path] = typer.Option(
        None,
        "--download-dir",
        "-d",
        envvar="AAPP2FACE_DOWNLOAD_DIR",
        show_envvar=False,
        show_default=False,
        help="Ruta donde se alojarán los archivos descargados.",
        exists=True,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Muestra la versión de la aplicación y sale.",
        is_eager=True,
    ),
):
    """AAPP2FACe command line interface"""

    NEUTRAL_COMMANDS = ("genresp", "config", "init")

    if config_file:
        rprint(f"Usando archivo de configuración: {config_file}")
        if not config_file.exists() and ctx.invoked_subcommand != "init":
            rprint(
                f"[red]No existe el archivo de configuración[/red] {config_file} [red]!![/red]"
            )
            raise (typer.Exit(1))
    else:
        config_file = get_config_path().joinpath(CONFIG_FILENAME)

    config = get_default_config()
    config.read(config_file)

    if url_prod:
        config["FACe"]["url_prod"] = url_prod

    if url_staging:
        config["FACe"]["url_staging"] = url_staging

    if use_staging is not None:
        config["FACe"]["use_staging"] = str(use_staging)

    if cert_file:
        config["X509"]["cert_file"] = str(cert_file)

    if key_file:
        config["X509"]["key_file"] = str(key_file)

    if download_dir:
        config["App"]["download_dir"] = str(download_dir)

    if fake_set:
        config["Fake"]["responses_dir"] = fake_set
        fake = True

    if fake:
        if not ctx.invoked_subcommand in NEUTRAL_COMMANDS:
            err_rprint(
                f"[warning]Aviso:[/warning] Usando entorno de simulación. Algunos parámetros de configuración serán ignorados."
            )
        client = FACeFakeSoapClient(Path(config["Fake"]["responses_dir"]))
    else:
        if config.getboolean("FACe", "use_staging"):
            url = config["FACe"]["url_staging"]
            if not ctx.invoked_subcommand in NEUTRAL_COMMANDS:
                err_rprint(
                    f"[warning]Aviso:[/warning] Usando entorno de pruebas de FACe (STAGING)."
                )
        else:
            url = config["FACe"]["url_prod"]

        client = FACeSoapClient(
            url,
            config["X509"]["cert_file"],
            config["X509"]["key_file"],
            debug=config["Debug"]["enabled"],
            log_path=config["Debug"]["log_dir"],
        )

    ctx.obj = AppData(config_file, config, FACeConnection(client))


if __name__ == "__main__":
    app()
