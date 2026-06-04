from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from tinydb import TinyDB, Query
import os
from datetime import datetime

app = Flask(
    __name__,
    template_folder="templates1",
    static_folder="static1"
)

app.secret_key = "tajni_kljuc_zapiski"


# -----------------------------
# Inicializacija baz
# -----------------------------
def init_db():
    if not os.path.exists("db"):
        os.makedirs("db")

    # Ločena baza za uporabnike in zapiske
    TinyDB("db/users_db.json").close()
    TinyDB("db/notes_db.json").close()


def get_users_db():
    """Baza za uporabnike."""
    return TinyDB("db/users_db.json")


def get_notes_db():
    """Baza za zapiske."""
    return TinyDB("db/notes_db.json")


# -----------------------------
# Sinhrone rute (HTML strani)
# -----------------------------
@app.route("/")
def index():
    """Glavna stran – prikaz zapiskov za prijavljenega uporabnika."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_notes_db()
    Note = Query()
    notes = db.search(Note.user_id == session["user_id"])
    db.close()

    # Sortiraj po datumu (novejši prvi)
    notes = sorted(notes, key=lambda x: x.get("created_at", ""), reverse=True)

    # TinyDB uporablja doc_id, zato ga dodamo v objekt
    notes_with_id = []
    for n in notes:
        notes_with_id.append({
            "id": n.doc_id,
            "title": n.get("title", ""),
            "content": n.get("content", ""),
            "created_at": n.get("created_at", "")
        })

    return render_template("index.html", notes=notes_with_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Prijava uporabnika."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_users_db()
        User = Query()
        user = db.get(User.username == username)
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user.doc_id
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Napačno uporabniško ime ali geslo")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registracija novega uporabnika."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_users_db()
        User = Query()

        existing_user = db.get(User.username == username)
        if existing_user:
            db.close()
            return render_template("register.html", error="Uporabniško ime že obstaja")

        hashed_password = generate_password_hash(password)
        db.insert({"username": username, "password": hashed_password})
        db.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Odjava uporabnika."""
    session.clear()
    return redirect(url_for("login"))


# -----------------------------
# API rute (AJAX za zapiske)
# -----------------------------
@app.route("/api/notes/add", methods=["POST"])
def add_note():
    """Dodaj nov zapis (AJAX)."""
    if "user_id" not in session:
        return jsonify({"error": "Niste prijavljeni"}), 401

    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title or not content:
        return jsonify({"error": "Naslov in vsebina sta obvezna"}), 400

    db = get_notes_db()
    note_data = {
        "user_id": session["user_id"],
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat()
    }
    note_id = db.insert(note_data)
    db.close()

    return jsonify({
        "id": note_id,
        "title": title,
        "content": content,
        "created_at": note_data["created_at"]
    })


@app.route("/api/notes/<int:note_id>/edit", methods=["PUT"])
def edit_note(note_id):
    """Uredi obstoječ zapis (AJAX)."""
    if "user_id" not in session:
        return jsonify({"error": "Niste prijavljeni"}), 401

    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    db = get_notes_db()
    note = db.get(doc_id=note_id)

    if not note or note.get("user_id") != session["user_id"]:
        db.close()
        return jsonify({"error": "Nimate dostopa do tega zapiska"}), 403

    db.update({"title": title, "content": content}, doc_ids=[note_id])
    db.close()

    return jsonify({"success": True})


@app.route("/api/notes/<int:note_id>/delete", methods=["DELETE"])
def delete_note(note_id):
    """Izbriši zapis (AJAX)."""
    if "user_id" not in session:
        return jsonify({"error": "Niste prijavljeni"}), 401

    db = get_notes_db()
    note = db.get(doc_id=note_id)

    if not note or note.get("user_id") != session["user_id"]:
        db.close()
        return jsonify({"error": "Nimate dostopa do tega zapiska"}), 403

    db.remove(doc_ids=[note_id])
    db.close()

    return jsonify({"success": True})


@app.route("/api/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    """Pridobi en zapis (AJAX)."""
    if "user_id" not in session:
        return jsonify({"error": "Niste prijavljeni"}), 401

    db = get_notes_db()
    note = db.get(doc_id=note_id)
    db.close()

    if not note or note.get("user_id") != session["user_id"]:
        return jsonify({"error": "Zapis ne obstaja"}), 404

    return jsonify({
        "id": note_id,
        "title": note.get("title", ""),
        "content": note.get("content", "")
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
