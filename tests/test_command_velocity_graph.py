from pathlib import Path

from sprint_velocity.main import app
from typer.testing import CliRunner
import datetime as dt

runner = CliRunner()


def test_velocity_graph_fails_on_missing_config_entries(tmp_config):
    result = runner.invoke(app, ["velocity-graph", "exampleCorps", "4568", "7893", "9876"])
    assert result.exit_code == 1


def test_velocity_graph_plain_success(tmp_config, mocked_response):
    runner.invoke(app, ["settings-board", "CapsuleCorp", "4568", "12456abcd", "https://jira.foobar.de"])
    runner.invoke(app, ["settings-board", "CapsuleCorp", "9876", "12456abcd", "https://jira.foobar.de"])

    result = runner.invoke(app, ["velocity-graph", "CapsuleCorp", "4568", "7893", "9876"])
    assert result.exit_code == 0
    # default file location is on the same folder
    # only
    file = Path(__file__).parent / Path("foobar", "mock.png")
    assert file.exists()
    file.unlink()


def test_velocity_graph_plain_use_config_filepath(tmp_config, mocked_response):
    runner.invoke(app, ["settings-filestorage", "/tmp/sprint_velocity/tests/filesstorage"])
    runner.invoke(app, ["settings-backupfile", "/tmp/sprint_velocity/tests/backup", "%Y%m%d"])

    runner.invoke(app, ["settings-board", "CapsuleCorp", "4568", "12456abcd", "https://jira.foobar.de"])
    runner.invoke(app, ["settings-board", "CapsuleCorp", "9876", "12456abcd", "https://jira.foobar.de"])

    result = runner.invoke(app, ["velocity-graph", "CapsuleCorp", "4568", "7893", "9876"])
    assert result.exit_code == 0

    file = Path("/", "tmp", "sprint_velocity", "tests", "filesstorage") / Path("foobar", "mock.png")
    assert file.exists()
    file.unlink()

    result = runner.invoke(app, ["velocity-graph", "CapsuleCorp", "4568", "7893", "9876"])
    assert result.exit_code == 0

    current_date = dt.date.today().strftime("%Y%m%d")
    file = Path("/", "tmp", "sprint_velocity", "tests", "backup") / Path(f"mock_{current_date}.png")
    assert file.exists()
    file.unlink()
