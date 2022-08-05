import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from sprint_velocity import utils
from sprint_velocity.config import Settings


@pytest.fixture(scope="function")
def tmp_config(monkeypatch):
    named_temp_file = NamedTemporaryFile(prefix="config_", suffix=".json")
    temp_file = named_temp_file.name
    monkeypatch.setattr(Settings, "CONFIG_FILE", temp_file)
    yield temp_file
    Path(temp_file).unlink(missing_ok=True)


@pytest.fixture(scope="function")
def mocked_response(monkeypatch):
    def mocked_json_response(*args, **kwargs):
        class MockedResponse:
            def json(self):
                return {
                    "values": [
                        {
                            "key": "foobar",
                            "state": "active",
                            "id": 4224,
                            "startDate": "2022-10-10",
                            "name": "mock",
                        }
                    ],
                    "total": 3,
                    "issues": [
                        {
                            "fields": {
                                "created": "2022-08-12T10:50:39.000+0200",
                                "updated": "2022-08-12T10:50:39.000+0200",
                                "status": {
                                    "statusCategory": {"key": "indeterminate", "name": "process"},
                                    "name": "process",
                                },
                            },
                        },
                        {
                            "fields": {
                                "created": "2022-08-13T10:50:39.000+0200",
                                "updated": "2022-08-13T10:50:39.000+0200",
                                "status": {
                                    "statusCategory": {"key": "indeterminate", "name": "process"},
                                    "name": "process",
                                },
                            },
                        },
                        {
                            "fields": {
                                "created": "2022-08-14T10:50:39.000+0200",
                                "updated": "2022-08-14T10:50:39.000+0200",
                                "status": {
                                    "statusCategory": {"key": "indeterminate", "name": "process"},
                                    "name": "process",
                                },
                            }
                        },
                    ],
                }

        return MockedResponse()

    monkeypatch.setattr(utils, "request", mocked_json_response)
    yield


def get_tmp_config(file: str):
    with Path(file).open("r") as file:
        return json.load(file)
