from dataclasses import dataclass, fields, astuple, asdict
from base64 import b64decode
from werkzeug.exceptions import HTTPException
from hashlib import sha256


class BadRequest(HTTPException):
    code = 400

    def __init__(self, desc):
        super().__init__(description=desc)


@dataclass
class Player:
    id: int
    name: str
    sex: str
    email: str
    picture_path: str

    n_sessions: int = 0
    n_wins: int = 0
    n_loses: int = 0
    seconds_in_game: int = 0

    @staticmethod
    def mutable_fields():
        return ["name", "sex", "email"]

    @staticmethod
    def pic_path(data: bytes):
        return f"pictures/{sha256(data).hexdigest()}.png"

    @classmethod
    def select(cls, conn, id):
        row = conn.execute("select * from players where id = ?", (id,)).fetchone()
        if row is None:
            raise KeyError("no such player")
        return cls(*row)

    @staticmethod
    def exists(conn, id):
        row = conn.execute("select count(*) from players where id = ?", (id,)).fetchone()
        return row[0] > 0

    def update(self, conn):
        astuple_with_id = astuple(self)[1:] + (self.id,)
        statement = "update players set " \
            + " , ".join(f"{f} = ?" for f in self.field_names()) \
            + " where id = ?"
        print(statement, astuple_with_id)
        conn.execute(
            statement,
            astuple_with_id,
        )
        conn.commit()

    def create(self, conn):
        field_names = ",".join(self.field_names())
        questions = ",".join(["?"] * len(self.field_names()))
        stmt = f"insert into players ({field_names}) values ({questions})"
        id = conn.execute(
            stmt,
            astuple(self)[1:],
        ).lastrowid
        conn.commit()
        return id

    @classmethod
    def field_names(cls):
        return [f.name for f in fields(cls) if f.name != "id"]

    @classmethod
    def fields(cls):
        return [f for f in fields(cls)]

    def as_dict(self):
        return asdict(self)

    @classmethod
    def _check_dict(cls, data, fail_on_missing=False):
        checked_data = {}
        for field in cls.fields():
            if field.name in cls.mutable_fields():
                if field.name not in data:
                    if fail_on_missing:
                        raise BadRequest(f"required field '{field.name}' is missing")
                    else:
                        continue
                if not isinstance(data[field.name], field.type):
                    raise BadRequest(f"required field '{field.name}' has wrong type")
                else:
                    checked_data[field.name] = data[field.name]

        if "picture" not in data:
            if fail_on_missing:
                raise BadRequest("picture is not present")
        else:
            pic = data["picture"]
            try:
                pic = b64decode(pic)
            except:
                raise BadRequest("failed to decode image")

            path = cls.pic_path(pic)
            with open(path, "wb") as f:
                f.write(pic)
            checked_data["picture_path"] = path

        return checked_data

    def update_from_dict_checked(self, conn, data):
        """
        type-checked update from dict
        """
        checked_data = self._check_dict(data)
        for name, val in checked_data.items():
            setattr(self, name, val)

        self.update(conn)

    @classmethod
    def from_dict_checked(cls, conn, data):
        checked_data = cls._check_dict(data, fail_on_missing=True)
        checked_data["id"] = -1

        player = Player(**checked_data)
        player.id = player.create(conn)
        return player
