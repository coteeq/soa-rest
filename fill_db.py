import sqlite3
from app.player import Player
from faker import Faker
import requests
from tqdm import trange
from io import BytesIO
from PIL import Image
import random
import click
from dataclasses import fields


def generate_pic():
    pic_response = requests.get("https://thiscatdoesnotexist.com")
    pic = Image.open(BytesIO(pic_response.content))
    pic.resize((256, 256))
    path = Player.pic_path(pic.tobytes())
    with open(path, "wb") as f:
        pic.save(f)
    return path


def ensure_table(conn):
    player_fields = fields(Player)

    def pytype_to_sql(tp):
        if isinstance(tp(), int):
            return "int"
        elif isinstance(tp(), str):
            return "text"

    conn.execute(
        """
        create table if not exists players (
            id integer primary key autoincrement,
        """
        + ",".join(
            f"{f.name} {pytype_to_sql(f.type)}" for f in player_fields if f.name != "id"
        )
        + ");"
    )


@click.command()
@click.option("--force", default=False, is_flag=True, help="Fill even if not empty")
@click.option("-n", default=10, help="number of players")
def main(force, n):
    conn = sqlite3.connect("players.db")
    ensure_table(conn)
    is_empty = conn.execute("select count(*) from players").fetchone()[0] == 0
    if not is_empty and not force:
        raise RuntimeError("Use --force to fill non-empty db")

    fake = Faker()
    Faker.seed(42)
    for _ in trange(n):
        profile = fake.simple_profile()
        sessions = random.randint(0, 1000)
        wins = random.randint(0, sessions)
        player = Player(
            id=-1,
            name=profile["username"],
            sex=profile["sex"],
            email=profile["mail"],
            picture_path=generate_pic(),
            n_sessions=sessions,
            n_wins=wins,
            n_loses=sessions - wins,
            seconds_in_game=random.randint(0, 10000),
        )

        player.create(conn)


if __name__ == "__main__":
    main()
