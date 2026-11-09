import os
import sqlite3
from contextlib import closing

from flask import Flask, redirect, render_template, request, url_for
from prometheus_flask_exporter import PrometheusMetrics


def create_app():
    app = Flask(__name__)
    db_path = os.environ.get("DB_PATH", "data/tasks.db")
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    def connect():
        db = sqlite3.connect(db_path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    with closing(connect()) as db, db:
        db.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )""")

    PrometheusMetrics(app)  # Ajoute /metrics pour Prometheus.

    @app.get("/")
    def index():
        with closing(connect()) as db:
            tasks = db.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        return render_template("index.html", tasks=tasks)

    @app.post("/tasks")
    def add_task():
        title = request.form.get("title", "").strip()
        if title and len(title) <= 120:
            with closing(connect()) as db, db:
                db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        with closing(connect()) as db, db:
            db.execute("""UPDATE tasks
                SET done = CASE WHEN done = 0 THEN 1 ELSE 0 END
                WHERE id = ?""", (task_id,))
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        with closing(connect()) as db, db:
            db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return redirect(url_for("index"))

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
