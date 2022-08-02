import dataclasses
import datetime
import json
import shutil
from json import JSONDecodeError
from pathlib import Path
from typing import Union

import pendulum
import typer
from requests import request
from requests.structures import CaseInsensitiveDict
from strongtyping.strong_typing import match_class_typing
from strongtyping.strong_typing import match_typing

from sprint_velocity.plot_matplolib import generate_plot


@match_typing
def create_dates(start_end: datetime.date, end_date: datetime.date):
    period = pendulum.period(start=start_end, end=end_date)
    for dt in period.range("days"):
        if dt.weekday() not in (5, 6):
            yield dt


def current_date():
    return datetime.date.today()


def get_json_data() -> dict:
    with Path("config.json").open("r") as file:
        try:
            return json.load(file)
        except JSONDecodeError:
            return {}


@match_typing
def save_json_data(json_data: dict):
    with Path("config.json").open("w") as file:
        json.dump(json_data, file)


@match_typing
def get_header(token: str) -> dict:
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    if not token:
        if token_ := get_json_data().get("token"):
            headers["Authorization"] = f"Bearer {token_}"
        else:
            typer.secho("No Token in settings!!!", fg=typer.colors.RED)
            typer.secho(
                "Please add a token to the settings via [settings_token <token>]",
                fg=typer.colors.GREEN,
            )
            raise typer.Abort
    else:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@match_typing
def get_current_sprint_info(url: str, board_id: int, headers: dict):
    base_url = f"{url}/agile/1.0/board/{board_id}/sprint"
    response = request("GET", url=base_url, headers=headers)

    for obj in response.json()["values"]:
        if obj["state"] == "active":
            return {
                "id": obj["id"],
                "start_date": obj["startDate"].split("T")[0],
                "name": obj["name"].lower().replace(" ", "_"),
            }


@match_typing
def get_project(url: str, board_id: int, headers):
    base_url = f"{url}/agile/1.0/board/{board_id}/project"
    response = request("GET", url=base_url, headers=headers)
    values = response.json()["values"]
    return values[0]["key"]


def display_settings(data: dict, tab_level: int = 0):
    idx = 0
    tab = "\t" * tab_level
    for key, val in data.items():
        color = typer.colors.GREEN if idx % 2 == 0 else typer.colors.CYAN
        if isinstance(val, dict):
            typer.secho(f"{tab}{key}: ", fg=color)
            display_settings(val, tab_level=tab_level + 1)
        else:
            typer.secho(f"{tab}{key}: {val}", fg=color)
        idx += 1


@match_class_typing
@dataclasses.dataclass
class StatisticFileProcess:
    file_root: Path
    sprint_name: str
    sprint_start_date: str
    config_data: dict
    json_response: Union[list, dict]


def process_file(file_process: StatisticFileProcess):
    outputfile = file_process.file_root / Path(file_process.sprint_name)

    if not file_process.file_root.exists():
        file_process.file_root.mkdir(parents=True)

    if backup_file_path := file_process.config_data.get("backup_file_path"):
        new_file = Path(f"{outputfile}.png")
        if new_file.exists():
            filename = outputfile.split("/")[-1]
            date_str = datetime.date.today().strftime(file_process.config_data.get("date_format", "%Y-%m-%d"))
            backup_file = Path(backup_file_path) / Path(f"{filename}_{date_str}.png")
            shutil.copy(new_file, backup_file)

    generate_plot(file_process.json_response, file_process.sprint_start_date, outputfile)

    typer.echo(f"Plot was saved under {outputfile}.png")
