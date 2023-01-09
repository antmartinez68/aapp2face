from typer.testing import CliRunner

from aapp2face import __version__
from aapp2face.cli.main import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"AAPP2FACe CLI Version: {__version__}" in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AAPP2FACe command line interface" in result.stdout
