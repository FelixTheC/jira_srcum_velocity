import urllib.parse
from pathlib import Path
from typing import List
from typing import Optional

import typer
from requests import request

from sprint_velocity.utils import (
    DATETIME_HELP,
    complete_date_format,
    display_settings,
    get_current_sprint_info,
    get_header,
    get_json_data,
    get_project,
    save_json_data,
)

app = typer.Typer()


@app.command()
def settings_backupfile(
    backup_file_path: Path = typer.Argument(
        ..., show_default=False, help="The path to your backup folder."
    ),
    date_format: str = typer.Argument(
        help=DATETIME_HELP, default="%Y-%m-%d_%H_%M_%S", autocompletion=complete_date_format
    ),
):
    json_data = get_json_data()
    json_data["backup_file_path"] = backup_file_path.as_posix()
    json_data["date_format"] = date_format
    save_json_data(json_data)


@app.command()
def settings_filestorage(
    file_path: Path = typer.Argument(
        ..., show_default=False, help="The path where your files should be stored."
    )
):
    json_data = get_json_data()
    json_data["file_path"] = file_path.as_posix()
    save_json_data(json_data)


@app.command()
def settings_board(
    company: str = typer.Argument(
        ..., show_default=False, help="The name of the company the board is from. Example: adesso"
    ),
    board_id: int = typer.Argument(
        ...,
        show_default=False,
        help="The id of the board. "
        "You can find these inside of the url "
        "`https://jira.foobar.de/secure/RapidBoard.jspa?rapidView=1234` "
        "it is the value of the `rapidView` => 1234.",
    ),
    token: str = typer.Argument(
        ...,
        show_default=False,
        help="The token can be generated in your profile section inside your jira.",
    ),
    url: str = typer.Argument(
        ..., show_default=False, help="The url of your board/jira server. https://jira.foobar.de"
    ),
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
def velocity_graph(
    company: str = typer.Argument(
        ..., show_default=False, help="The company name you used in settings."
    ),
    board_ids: Optional[List[int]] = typer.Argument(
        None,
        show_default=False,
        help="If specified it will only create plots for the selected board_ids "
        "otherwise all board_ids belonging to the selected company will be created.",
    ),
):
    json_data = get_json_data()
    if not (company_data := json_data.get(company)):
        typer.secho(
            f"Please create settings for {company} via `jira_statistics settings-board --help`.",
            fg=typer.colors.RED,
        )
        raise typer.Abort

    ids = board_ids if board_ids else []

    for board_id in company_data:
        if ids and int(board_id) not in ids:
            continue

        int_board_id = int(board_id)
        token = company_data[board_id]["token"]
        url = company_data[board_id]["url"]

        headers = get_header(token)
        project = get_project(url, int_board_id, headers)
        sprint_info = get_current_sprint_info(url, int_board_id, headers)
        sprint_start_date = sprint_info["start_date"]

        search_str = f"project = {project} and issuetype in subTaskIssueTypes() AND Sprint = {sprint_info['id']} AND (resolution = unresolved or resolved >= {sprint_start_date})"  # noqa: E501
        search_query = urllib.parse.quote(search_str)

        base_url = f"{url}/api/2/search?jql={search_query}"
        response = request("GET", url=base_url, headers=headers)

        file_root = Path(json_data.get("file_path", ""), project)
        if not json_data.get("file_path"):
            typer.secho(
                "For a custom file path run `jira_statistics settings-filestorage --help`.",
                fg=typer.colors.BRIGHT_MAGENTA,
            )
        outputfile = file_root / Path(sprint_info["name"])
        if not file_root.exists():
            file_root.mkdir(parents=True)

        if backup_file_path := json_data.get("backup_file_path"):

            new_file = Path(f"{outputfile}.png")
            if new_file.exists():
                if not Path(backup_file_path).exists():
                    Path(backup_file_path).mkdir(parents=True)

                filename = outputfile.name
                date_str = datetime.datetime.now().strftime(
                    json_data.get("date_format", "%Y-%m-%d")
                )
                backup_file = Path(backup_file_path) / Path(f"{filename}_{date_str}.png")
                shutil.copy(new_file, backup_file)

        generate_plot(response.json(), sprint_start_date, outputfile)

        typer.echo(f"Plot was saved under {outputfile}.png")

    typer.echo("All plots processed.")


if __name__ == "__main__":
    app(["display-config"])
