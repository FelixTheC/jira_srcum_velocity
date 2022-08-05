from sprint_velocity.main import app
from typer.testing import CliRunner

from tests.conftest import get_tmp_config

runner = CliRunner()


def test_set_all_settings(tmp_config):
    runner.invoke(app, ["settings-backupfile", "/tmp/backupfiles", "%Y%m%d"])
    runner.invoke(app, ["settings-filestorage", "/tmp/filesstorage"])
    runner.invoke(app, ["settings-board", "capsule-corps", "987654", "bu1m4", "https://jira.capsule.de"])
    runner.invoke(app, ["settings-project", "exampleCorps", "foobar", "12456abcd", "https://jira.foobar.de"])
    runner.invoke(app, ["settings-add-sprint-to-project", "exampleCorps", "foobar", "7893", "2022-10-10"])

    tmp_json_config = get_tmp_config(tmp_config)

    assert tmp_json_config["capsule-corps"]["987654"]["token"] == "bu1m4"
    assert tmp_json_config["capsule-corps"]["987654"]["url"] == "https://jira.capsule.de/rest"
    assert tmp_json_config["exampleCorps"]["foobar"]["7893"] == "2022-10-10"
