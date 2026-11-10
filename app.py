import os, sqlite3
from flask import Flask, g, render_template, request, redirect, url_for

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "/data/tasks.db")


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "priority TEXT NOT NULL DEFAULT 'medium',"
            "done INTEGER NOT NULL DEFAULT 0)"
        )


@app.route("/")
def index():
    show = request.args.get("show", "all")
    sql = "SELECT * FROM tasks"
    if show == "open":
        sql += " WHERE done = 0"
    elif show == "done":
        sql += " WHERE done = 1"
    tasks = db().execute(sql + " ORDER BY done, id DESC").fetchall()
    return render_template("index.html", tasks=tasks, show=show)


@app.post("/add")
def add():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")
    if title and priority in ("low", "medium", "high"):
        db().execute("INSERT INTO tasks (title, priority) VALUES (?, ?)", (title, priority))
        db().commit()
    return redirect(url_for("index"))


@app.post("/toggle/<int:task_id>")
def toggle(task_id):
    db().execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
    db().commit()
    return redirect(request.referrer or url_for("index"))


@app.post("/delete/<int:task_id>")
def delete(task_id):
    db().execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db().commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/stats")
def stats():
    row = db().execute(
        "SELECT COUNT(*) total, COALESCE(SUM(done),0) done FROM tasks"
    ).fetchone()
    by_priority = db().execute(
        "SELECT priority, COUNT(*) n FROM tasks WHERE done = 0 GROUP BY priority"
    ).fetchall()
    return render_template("stats.html", total=row["total"], done=row["done"],
                           by_priority={r["priority"]: r["n"] for r in by_priority})


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/health")
def health():
    return {"status": "ok"}


init_db()
