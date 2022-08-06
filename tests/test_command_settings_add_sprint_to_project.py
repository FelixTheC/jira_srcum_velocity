from typer.testing import CliRunner

from sprint_velocity.main import app
from tests.conftest import get_tmp_config

runner = CliRunner()


def test_settings_project_fails_on_missing_project(tmp_config):
    result = runner.invoke(
        app, ["settings-add-sprint-to-project", "exampleCorps", "foobar", "7893", "2022-10-10"]
    )
    assert result.exit_code == 1


def test_settings_project_success(tmp_config):
    result = runner.invoke(
        app, ["settings-project", "exampleCorps", "foobar", "12456abcd", "https://jira.foobar.de"]
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app, ["settings-add-sprint-to-project", "exampleCorps", "foobar", "7893", "2022-10-10"]
    )

    assert result.exit_code == 0
    json_config = get_tmp_config(tmp_config)
    assert json_config["exampleCorps"]["foobar"]["7893"] == "2022-10-10"
