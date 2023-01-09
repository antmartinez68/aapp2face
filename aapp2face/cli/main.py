"""
Módulo CLI de AAPP2FACe
"""

from typing import Optional

import typer

from aapp2face import __version__

app = typer.Typer(no_args_is_help=True)


def version_callback(value: bool):
    """Callback de mostrado de la versión"""

    if value:
        print(f"AAPP2FACe CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        help="Muestra la versión de la aplicación y sale.",
        is_eager=True,
    ),
):
    """AAPP2FACe command line interface"""


if __name__ == "__main__":
    app()
