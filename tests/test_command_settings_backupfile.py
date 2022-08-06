import typer
from typer.testing import CliRunner

from sprint_velocity.main import settings_backupfile
from tests.conftest import get_tmp_config

runner = CliRunner()

app = typer.Typer()


def test_settings_backupfile_success(tmp_config):
    app.command()(settings_backupfile)
    result = runner.invoke(app, ["/tmp/backupfiles", "%Y%m%d"])
    assert result.exit_code == 0

    tmp_json_config = get_tmp_config(tmp_config)
    assert tmp_json_config["backup_file_path"] == "/tmp/backupfiles"
    assert tmp_json_config["date_format"] == "%Y%m%d"
