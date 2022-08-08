from pathlib import Path

import pytest
from typer.testing import CliRunner

from sprint_velocity.main import app

runner = CliRunner()


def test_velocity_graph_plain_fails_on_missing_project(tmp_config):
    result = runner.invoke(app, ["velocity-graph-plain", "exampleCorps", "foobar", "7893"])
    assert result.exit_code == 1


@pytest.mark.skip(reason="Works not correct on github.")
def test_velocity_graph_plain_success(tmp_config, mocked_response):
    runner.invoke(
        app, ["settings-project", "exampleCorps", "foobar", "12456abcd", "https://jira.foobar.de"]
    )
    runner.invoke(
        app, ["settings-add-sprint-to-project", "exampleCorps", "foobar", "7893", "2022-07-10"]
    )

    result = runner.invoke(app, ["velocity-graph-plain", "exampleCorps", "foobar", "7893"])
    assert result.exit_code == 0
    # default file location is on the same folder
    file = Path(__file__).parent / Path("foobar", "7893.png")
    assert file.exists()
    file.unlink()


def test_velocity_graph_plain_use_config_filepath(tmp_config, mocked_response):
    runner.invoke(app, ["settings-filestorage", "/tmp/sprint_velocity/tests/filesstorage"])

    runner.invoke(
        app, ["settings-project", "exampleCorps", "foofoo", "12456abcd", "https://jira.foobar.de"]
    )
    runner.invoke(
        app, ["settings-add-sprint-to-project", "exampleCorps", "foofoo", "2142", "2022-07-10"]
    )

    result = runner.invoke(app, ["velocity-graph-plain", "exampleCorps", "foofoo", "2142"])
    assert result.exit_code == 0

    file = Path("/", "tmp", "sprint_velocity", "tests", "filesstorage") / Path("foofoo", "2142.png")
    assert file.exists()
    file.unlink()
