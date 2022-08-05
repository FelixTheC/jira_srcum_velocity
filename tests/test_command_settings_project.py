import typer
from sprint_velocity.main import settings_project
from typer.testing import CliRunner

from tests.conftest import get_tmp_config

runner = CliRunner()

app = typer.Typer()


def test_settings_project(tmp_config):
    app.command()(settings_project)
    result = runner.invoke(app, ["exampleCorps", "foobar", "12456abcd", "https://jira.foobar.de"])
    assert result.exit_code == 0

    tmp_json_config = get_tmp_config(tmp_config)
    assert tmp_json_config["exampleCorps"]["foobar"]["token"] == "12456abcd"
    assert tmp_json_config["exampleCorps"]["foobar"]["url"] == "https://jira.foobar.de/rest"
