"""
Módulo con funciones de apoyo a la CLI
"""

import sys
from pathlib import Path
from typing import Any

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
