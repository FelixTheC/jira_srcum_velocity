import datetime
from itertools import accumulate

import matplotlib.pyplot as plt
import pandas as pd
from strongtyping.config import SEVERITY_LEVEL
from strongtyping.strong_typing import match_typing


@match_typing(severity=SEVERITY_LEVEL.WARNING)
def generate_plot(json_data: dict, sprint_start_date: str, outputfile, sprint_interval: int = 14):
    from sprint_velocity.utils import create_dates, current_date

    data = []
    sprint_start = datetime.datetime.strptime(sprint_start_date, "%Y-%m-%d").date()
    sprint_end = sprint_start + datetime.timedelta(days=sprint_interval)
    dates = list(create_dates(sprint_start, sprint_end))
    open_issues_dates = list(create_dates(sprint_start, current_date()))

    try:
        date_today = dates.index(current_date())
    except ValueError:
        date_today = None

    title = f"Sprint from {sprint_start}: Issues"
    total = json_data["total"]
    issues = json_data["issues"]

    plt.figure()
    plt.title(title)

    for issue in issues:
        created = issue["fields"]["created"]
        resolutiondate = issue["fields"]["resolutiondate"]
        status = issue["fields"]["status"]["statusCategory"]["key"]
        status_name = issue["fields"]["status"]["name"]
        data.append(
            {
                "created": created,
                "status": status,
                "status_name": status_name,
                "resolutiondate": resolutiondate,
            }
        )
    df = pd.DataFrame(data)

    df["created"] = pd.to_datetime(df["created"])
    df["resolutiondate"] = pd.to_datetime(df["resolutiondate"])

    df_sprint = df[(df["resolutiondate"].dt.date >= sprint_start) & (df["status"] == "done")]
    df_resolved_count = df_sprint.groupby(df_sprint["resolutiondate"].dt.date)["status"].count()

    resolved_values = [
        df_resolved_count.get(datetime.date.fromordinal(obj.toordinal()), 0)
        for obj in open_issues_dates
    ]
    if resolved_values:
        resolved_values[0] = total - resolved_values[0]
    else:
        resolved_values.append(total)

    stepper_x = list(range(len(open_issues_dates)))[: len(resolved_values)]
    stepper_y = list(accumulate(resolved_values, lambda x_, y_: x_ - y_))

    plt.step(x=stepper_x, y=stepper_y, color="r", label="Issues Open")

    df_after_sprint_start = df[df["created"].dt.date >= sprint_start]
    df_after_sprint_start_count = df_after_sprint_start.groupby(
        df_after_sprint_start["created"].dt.date
    )["created"].count()

    bar_x = list(range(len(dates)))
    bar_height = [
        df_after_sprint_start_count.get(datetime.date.fromordinal(obj.toordinal()), 0)
        for obj in dates
    ]

    plt.bar(bar_x, bar_height, color="silver", label="In Sprint Added")
    plt.ylabel("Issues")

    sprint_days = list(range(len(dates)))
    # count down by percentage
    results = [total * (1 - (idx * 0.1)) for idx in sprint_days]

    plt.plot(sprint_days, results, color="navy", label="Base Line")

    if date_today:
        plt.plot(
            [date_today, date_today],
            [total + 5, 0],
            color="black",
            linestyle="dashed",
            label="Current Sprint-Date",
        )

    # plt.xticks(x, dates, rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{outputfile}.png", format="png")
