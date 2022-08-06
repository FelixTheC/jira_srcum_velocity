from pathlib import Path

from typer.testing import CliRunner

from sprint_velocity.main import app

runner = CliRunner()


def test_config_created_on_startup():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    file = Path(__file__).parent / Path("config.json")
    assert file.exists()
    file.unlink()
