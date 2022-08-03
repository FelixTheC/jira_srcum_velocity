import urllib.parse
from pathlib import Path
from typing import List
from typing import Optional

import typer
from requests import request

from sprint_velocity.utils import StatisticFileProcess, create_initial_json
from sprint_velocity.utils import display_settings
from sprint_velocity.utils import get_current_sprint_info
from sprint_velocity.utils import get_header
from sprint_velocity.utils import get_json_data
from sprint_velocity.utils import get_project
from sprint_velocity.utils import process_file
from sprint_velocity.utils import save_json_data

app = typer.Typer()
create_initial_json()


@app.command()
def settings_backupfile(backup_file_path: Path, date_format: str):
    json_data = get_json_data()
    json_data["backup_file_path"] = backup_file_path.as_posix()
    json_data["date_format"] = date_format
    save_json_data(json_data)


@app.command()
def settings_filestorage(file_path: Path):
    json_data = get_json_data()
    json_data["file_path"] = file_path.as_posix()
    save_json_data(json_data)


@app.command()
def settings_board(
        company: str,
        board_id: int,
        token: str,
        url: str = typer.Argument(..., help="https://jira.foo.de"),
):
    json_data = get_json_data()
    current = json_data.get(company, {})
    json_data[company] = {board_id: {"token": token, "url": f"{url}/rest"}, **current}
    save_json_data(json_data)


@app.command()
def settings_project(
        company: str,
        project: str,
        token: str,
        url: str = typer.Argument(..., help="https://jira.foo.de"),
):
    json_data = get_json_data()
    current = json_data.get(company, {})
    json_data[company] = {project: {"token": token, "url": f"{url}/rest"}, **current}
    save_json_data(json_data)


@app.command()
def settings_add_sprint_to_project(
        company: str,
        project: str,
        sprint_id: int,
        sprint_start_date: str
):
    json_data = get_json_data()
    try:
        json_data[company][project]
    except KeyError:
        typer.secho("Run `jira_statistics settings_project --help` first.")
        raise typer.Abort()
    json_data[company][project][sprint_id] = sprint_start_date
    save_json_data(json_data)


@app.command()
def display_config():
    json_data = get_json_data()
    display_settings(json_data)


@app.command()
def velocity_graph_plain(company: str, project: str, sprint_id: int):
    json_data = get_json_data()
    if not (company_data := json_data.get(company)):
        typer.secho(
            f"Please create a setting for {company} via settings_board.",
            fg=typer.colors.RED,
        )
        raise typer.Abort

    token = company_data[project]["token"]
    url = company_data[project]["url"]
    sprint_start_date = company_data[project][str(sprint_id)]

    headers = get_header(token)

    search_str = f"project = {project} and issuetype in subTaskIssueTypes() AND Sprint = {sprint_id} AND (resolution = unresolved or resolved >= {sprint_start_date})"  # noqa: E501
    search_query = urllib.parse.quote(search_str)
    base_url = f"{url}/api/2/search?jql={search_query}"
    response = request("GET", url=base_url, headers=headers)

    file_root = Path(json_data.get("file_path", ""), project)
    process_file(StatisticFileProcess(file_root=file_root,
                                      sprint_name=str(sprint_id),
                                      sprint_start_date=sprint_start_date,
                                      config_data=json_data,
                                      json_response=response.json()))


@app.command()
def velocity_graph(company: str, board_ids: Optional[List[int]] = typer.Argument(None)):
    json_data = get_json_data()
    if not (company_data := json_data.get(company)):
        typer.secho(
            f"Please create a setting for {company} via settings_board.",
            fg=typer.colors.RED,
        )
        raise typer.Abort

    ids = board_ids if board_ids else []

    for board_id in company_data:
        if ids and int(board_id) not in ids:
            continue

        token = company_data[board_id]["token"]
        url = company_data[board_id]["url"]

        headers = get_header(token)
        project = get_project(url, int(board_id), headers)
        sprint_info = get_current_sprint_info(url, int(board_id), headers)
        sprint_start_date = sprint_info["start_date"]

        search_str = f"project = {project} and issuetype in subTaskIssueTypes() AND Sprint = {sprint_info['id']} AND (resolution = unresolved or resolved >= {sprint_start_date})"  # noqa: E501
        search_query = urllib.parse.quote(search_str)

        base_url = f"{url}/api/2/search?jql={search_query}"
        response = request("GET", url=base_url, headers=headers)

        file_root = Path(json_data.get("file_path", ""), project)
        process_file(StatisticFileProcess(file_root=file_root,
                                          sprint_name=sprint_info["name"],
                                          sprint_start_date=sprint_start_date,
                                          config_data=json_data,
                                          json_response=response.json()))

    typer.echo("All plots processed.")


if __name__ == "__main__":
    app(["velocity-graph", "adesso", "4223"])
