"""
App3 – Glasbeni seznam (TinyDB)
Funkcionalnosti:
- Prikaz vseh pesmi
- Dodajanje nove pesmi
- Urejanje obstoječe pesmi
- Brisanje pesmi
"""

from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query
from datetime import datetime
import os

app = Flask(__name__, template_folder="templates3", static_folder="static3")


# -----------------------------
#  Pomožne funkcije
# -----------------------------

def get_db():
    """Vrne instanco TinyDB baze."""
    return TinyDB("db/music_db.json")


def init_db():
    """Ustvari mapo db, če še ne obstaja."""
    if not os.path.exists("db"):
        os.makedirs("db")
    db = get_db()
    db.close()


# -----------------------------
#  Glavne rute
# -----------------------------

@app.route("/")
def index():
    """Prikaže glavno HTML stran."""
    return render_template("index.html")


@app.route("/api/songs", methods=["GET"])
def get_songs():
    """Vrne seznam vseh pesmi, urejenih po datumu dodajanja."""
    db = get_db()
    Song = Query()

    songs = db.search(Song.type == "song")
    songs = sorted(songs, key=lambda x: x.get("created_at", ""), reverse=True)

    result = [
        {
            "id": s.doc_id,
            "title": s.get("title", ""),
            "artist": s.get("artist", ""),
            "album": s.get("album", ""),
            "created_at": s.get("created_at", "")
        }
        for s in songs
    ]

    db.close()
    return jsonify(result)


@app.route("/api/songs/add", methods=["POST"])
def add_song():
    """Doda novo pesem v bazo."""
    data = request.get_json() or {}

    title = (data.get("title") or "").strip()
    artist = (data.get("artist") or "").strip()
    album = (data.get("album") or "").strip()

    if not title:
        return jsonify({"error": "Naslov je obvezen"}), 400

    db = get_db()
    song = {
        "type": "song",
        "title": title,
        "artist": artist,
        "album": album,
        "created_at": datetime.now().isoformat()
    }

    song_id = db.insert(song)
    db.close()

    return jsonify({"id": song_id, **song})


@app.route("/api/songs/<int:song_id>/delete", methods=["DELETE"])
def delete_song(song_id):
    """Izbriše pesem po ID-ju."""
    db = get_db()

    if not db.get(doc_id=song_id):
        db.close()
        return jsonify({"error": "Vnos ne obstaja"}), 404

    db.remove(doc_ids=[song_id])
    db.close()

    return jsonify({"success": True})


@app.route("/api/songs/<int:song_id>/edit", methods=["PUT"])
def edit_song(song_id):
    """Uredi obstoječo pesem."""
    data = request.get_json() or {}

    title = (data.get("title") or "").strip()
    artist = (data.get("artist") or "").strip()
    album = (data.get("album") or "").strip()

    if not title:
        return jsonify({"error": "Naslov je obvezen"}), 400

    db = get_db()

    if not db.get(doc_id=song_id):
        db.close()
        return jsonify({"error": "Vnos ne obstaja"}), 404

    db.update(
        {"title": title, "artist": artist, "album": album},
        doc_ids=[song_id]
    )

    db.close()
    return jsonify({"success": True})


    
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5002)
