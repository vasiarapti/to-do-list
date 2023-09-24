import sqlite3

from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
app.config['DATABASE'] = 'todo.db'


# Function to get the database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


# Create the database table if it doesn't exist
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route("/")
def index():
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks").fetchall()
    return render_template("index.html", tasks=tasks)


@app.route("/add_task", methods=["POST"])
def add_task():
    task = request.form["task"]
    db = get_db()
    db.execute("INSERT INTO tasks (task, done) VALUES (?, ?)", (task, 0))
    db.commit()
    return redirect(url_for("index"))


@app.route("/mark_task_done/<int:task_id>")
def mark_task_done(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET done = ? WHERE id = ?", (1, task_id))
    db.commit()
    return redirect(url_for("index"))


@app.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
