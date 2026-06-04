from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from tinydb import TinyDB, Query
import os
from datetime import datetime

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2",
    static_url_path="/static2"
)

app.secret_key = "tajni_kljuc_socialna"

UPLOAD_FOLDER = "static2/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_users_db():
    return TinyDB("db/users_db.json")

def get_posts_db():
    return TinyDB("db/posts_db.json")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def init_db():
    if not os.path.exists("db"):
        os.makedirs("db")

    TinyDB("db/users_db.json").close()
    TinyDB("db/posts_db.json").close()


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
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

        return render_template("login.html", error="Napačno ime ali geslo")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_users_db()
        User = Query()

        if db.get(User.username == username):
            db.close()
            return render_template("register.html", error="Uporabnik obstaja")

        db.insert({
            "username": username,
            "password": generate_password_hash(password)
        })

        db.close()
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- HOME ----------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db_posts = get_posts_db()
    db_users = get_users_db()

    Post = Query()
    posts = db_posts.search(Post.type == "post")
    posts = sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)

    result = []
    for post in posts:
        author = db_users.get(doc_id=post["user_id"])

        result.append({
            "id": post.doc_id,
            "author": author["username"] if author else "Unknown",
            "content": post.get("content", ""),
            "image": post.get("image"),
            "created_at": post.get("created_at", "")
        })

    db_posts.close()
    db_users.close()

    return render_template("index.html", posts=result)


# ---------------- GET POSTS ----------------
@app.route("/api/posts")
def get_posts():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    db_posts = get_posts_db()
    db_users = get_users_db()

    Post = Query()
    posts = db_posts.search(Post.type == "post")
    posts = sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)

    result = []
    for post in posts:
        author = db_users.get(doc_id=post["user_id"])
        result.append({
            "id": post.doc_id,
            "author": author["username"] if author else "Unknown",
            "content": post.get("content", ""),
            "image": post.get("image"),
            "created_at": post.get("created_at", "")
        })

    db_posts.close()
    db_users.close()

    return jsonify(result)


# ---------------- ADD POST ----------------
@app.route("/api/posts/add", methods=["POST"])
def add_post():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    content = request.form.get("content")

    if not content:
        return jsonify({"error": "Empty content"}), 400

    image_path = None

    if "image" in request.files:
        file = request.files["image"]

        if file and allowed_file(file.filename):
            filename = secure_filename(
                f"{datetime.now().timestamp()}_{file.filename}"
            )
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = f"uploads/{filename}"

    db = get_posts_db()

    post_id = db.insert({
        "type": "post",
        "user_id": session["user_id"],
        "content": content,
        "image": image_path,
        "created_at": datetime.now().isoformat()
    })

    db.close()

    return jsonify({"success": True, "id": post_id})


# ---------------- DELETE POST ----------------
@app.route("/api/posts/<int:post_id>/delete", methods=["DELETE"])
def delete_post(post_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    db = get_posts_db()
    post = db.get(doc_id=post_id)

    if not post or post["user_id"] != session["user_id"]:
        db.close()
        return jsonify({"error": "No access"}), 403

    if post.get("image"):
        image_file = os.path.join(UPLOAD_FOLDER, os.path.basename(post["image"]))
        if os.path.exists(image_file):
            os.remove(image_file)

    db.remove(doc_ids=[post_id])
    db.close()

    return jsonify({"success": True})


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)