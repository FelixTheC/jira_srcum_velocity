import pytest
import typer
from sprint_velocity.main import settings_board
from typer.testing import CliRunner

from tests.conftest import get_tmp_config

runner = CliRunner()

app = typer.Typer()


def test_settings_board(tmp_config):
    app.command()(settings_board)
    result = runner.invoke(app, ["exampleCorps", "1234", "12456abcd", "https://jira.foobar.de"])
    assert result.exit_code == 0

    tmp_json_config = get_tmp_config(tmp_config)
    assert tmp_json_config["exampleCorps"]["1234"]["token"] == "12456abcd"
    assert tmp_json_config["exampleCorps"]["1234"]["url"] == "https://jira.foobar.de/rest"


@pytest.mark.parametrize("invalid_board_id", ("1$34", "123A", "42.21"))
def test_settings_board_board_id_must_int(tmp_config, invalid_board_id):
    app.command()(settings_board)
    result = runner.invoke(app, ["exampleCorps", invalid_board_id, "12456abcd", "https://jira.foobar.de"])
    assert result.exit_code == 2
