"""
Módulo con funciones de apoyo a la CLI
"""

import csv
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "field": "bold blue",
        "info": "bold green",
        "warning": "bold magenta",
        "error": "bold red",
        "data": "yellow",
    }
)

console = Console(highlight=False, theme=custom_theme)
err_console = Console(stderr=True, highlight=False, theme=custom_theme)


def rprint(*objects: Any, sep: str = " ", end: str = "\n") -> None:
    """Imprime objetos a través de una instancia personalizada de la clase `rich.console.Console`.

    Parameters
    ----------
    *objects: Any
        Objetos a imprimir posicionalmente.
    sep : str, optional
        Separador entre objetos impresos. Por defecto " ".
    end : str, optional
        Caracter a imprimir al final de la salida. Por defecto "\\n".
    """

    return console.print(*objects, sep=sep, end=end)


def err_rprint(*objects: Any, sep: str = " ", end: str = "\n") -> None:
    """Imprime objetos por la consola de errores.

    Parameters
    ----------
    *objects : Any
        Objetos a imprimir posicionalmente.
    sep : str, optional
        Separador entre objetos impresos. Por defecto " ".
    end : str, optional
        Caracter a imprimir al final de la salida. Por defecto "\\n".
    """

    return err_console.print(*objects, sep=sep, end=end)


def get_config_path() -> Path:
    """Devuelve la ruta y nombre de archivo para guardar configuración

    linux: ~/.config/aapp2face
    macOS: ~/Library/Application Support/aapp2face
    windows: C:/Users/<USER>/AppData/Roaming/aapp2face
    """

    home = Path.home()

    if sys.platform.startswith("win32"):
        return home / "AppData/Roaming/aapp2face"
    elif sys.platform.startswith("linux"):
        return home / ".config/aapp2face"
    elif sys.platform.startswith("darwin"):
        return home / "Library/Application Support/aapp2face"
    else:
        return home / "aapp2face"


def verify_export(export: Path | None) -> None:
    """Aborta la ejecución si no existe el archivo de exportación.

    Parameters
    ----------
    export : Path
        Archivo de exportación a comprobar
    """

    if export and export.exists():
        err_rprint(f"[error]Error:[/error] El archivo [data]{export}[/data] ya existe.")
        raise typer.Abort()


def export_data(
    data: list[dict], filename: Path, exclude_fields: list[str] = []
) -> None:
    """Exporta una lista de diccionarios a un archivo en formato CSV.

    Parameters
    ----------
    data : list[dict]
        Lista de diccionarios a imprimir.
    filename : Path
        Archivo destino de la exportación.
    exclude_fields : list[str], optional
        Lista de campos a excluir en la exportación. Por defecto ninguno.
    """

    fieldnames = [field for field in data[0].keys() if field not in exclude_fields]
    with open(filename, "x", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for d in data:
            row = {k: v for k, v in d.items() if k not in exclude_fields}
            writer.writerow(row)
