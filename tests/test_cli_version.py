from typer.testing import CliRunner

from aapp2face import __version__
from aapp2face.cli.main import app

runner = CliRunner()


def test_estados():
    expected_output = f"AAPP2FACe CLI Version: {__version__}"

    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert expected_output.replace("\n", "") in result.stdout.replace("\n", "")
