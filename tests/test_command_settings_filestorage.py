import typer
from sprint_velocity.main import settings_filestorage
from typer.testing import CliRunner

from tests.conftest import get_tmp_config

runner = CliRunner()

app = typer.Typer()


def test_settings_filestorage(tmp_config):
    app.command()(settings_filestorage)
    result = runner.invoke(app, ["/tmp/filesstorage"])
    assert result.exit_code == 0

    tmp_json_config = get_tmp_config(tmp_config)
    assert tmp_json_config["file_path"] == "/tmp/filesstorage"