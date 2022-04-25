from dataclasses import dataclass
from .player import Player
from shutil import move
import pdfkit




@dataclass
class CreatePdfTask:
    player: Player
    pdf_path: str


template = """
<style>
table {{
  border-collapse: collapse;
}}

td, th {{
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}}

tr:nth-child(even) {{
  background-color: #dddddd;
}}
</style>
<body style="font-family: monospace">
<h1><img src="http://localhost:5000/{player.picture_path}" height="100" />{player.name} stats</h1>
<hr>
<table>
    <tr>
        <th> name </th>
        <th> value </th>
    </tr>
    <tr>
        <td>sessions</td> <td>{player.n_sessions}</td>
    </tr>
    <tr>
        <td>wins</td> <td>{player.n_wins}</td>
    </tr>
    <tr>
        <td>loses</td> <td>{player.n_loses}</td>
    </tr>
    <tr>
        <td>time in game</td> <td>{time_in_game}</td>
    </tr>
</table>
</body>
"""


def secs_to_time(secs):
    if secs < 2 * 60:
        return f"{secs} seconds"
    if secs < 2 * 60 * 60:
        return f"{round(secs / 60)} minutes"
    if secs < 2 * 60 * 60 * 24:
        return f"{round(secs / 60 / 60)} hours"
    if secs < 2 * 60 * 60 * 24 * 7:
        return f"{round(secs / 60 / 60 / 24)} days"

    return f"{round(secs / 60 / 60 / 24 / 7)} weeks"


def create_pdf(task: CreatePdfTask):
    """
    Atomically places ready pdf into path `task.pdf_path`
    """
    tmp_path = task.pdf_path + ".processing"

    pdfkit.from_string(template.format(player=task.player, time_in_game=secs_to_time(task.player.seconds_in_game)), tmp_path)

    move(tmp_path, task.pdf_path)
