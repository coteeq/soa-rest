import sqlite3
from uuid import uuid4
from flask import Flask, jsonify, abort, request, g
from flask import send_from_directory


from app.gen_pdf import CreatePdfTask
from app.tasks import TaskWorker
from .player import Player

app = Flask("soa-mafia")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("players.db")
    return db

def get_worker():
    worker = getattr(g, '_worker', None)
    if worker is None:
        worker = g._worker = TaskWorker.run_forever()
    return worker


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.get("/players")
def get_players():
    """
    This method is not-so-resty, because it queries many resources in one query.
    So it takes player ids in queryargs
    """
    ids = request.args.getlist("id")
    try:
        players = [Player.select(get_db(), id).as_dict() for id in ids]
    except KeyError:
        abort(404)

    return jsonify({"players": players})


@app.get("/player/<string:id>")
def get_player(id):
    try:
        return jsonify(Player.select(get_db(), id).as_dict())
    except KeyError:
        abort(404)


@app.post("/player")
def post_player():
    if "id" not in request.json:
        id = Player.from_dict_checked(get_db(), request.json).id
    else:
        id = request.json["id"]
        if Player.exists(get_db(), id):
            Player.select(get_db(), id).update_from_dict_checked(get_db(), request.json)
        else:
            abort(404)

    return jsonify(id=id)


@app.put("/player")
def put_player():
    if not Player.exists(request.json["id"]):
        return post_player()
    player = Player.from_dict_checked(get_db(), request.json)
    return jsonify(id=player.id), 201

@app.post("/player_pdf/<id>")
def request_pdf(id):
    if not Player.exists(get_db(), id):
        abort(404)

    player = Player.select(get_db(), id)
    path = "pdfs/" + str(uuid4()) + ".pdf"
    get_worker().queue.put(CreatePdfTask(player=player, pdf_path=path))
    return jsonify(path=path)


@app.route('/pdfs/<path:path>')
def static_pdfs(path):
    return send_from_directory('pdfs', path)

@app.route('/pictures/<path:path>')
def static_picture(path):
    return send_from_directory('pictures', path)
