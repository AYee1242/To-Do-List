from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Setting up app to work with sqlalchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), unique=False, nullable=False)
    completed = db.Column(db.Boolean, unique=False, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)


@app.route("/")
def index():
    todo_list = Task.query.order_by(Task.due_date).all()
    return render_template("index.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    description = request.form.get("description")
    due_date = request.form.get("due_date")

    # Dont add task if there is no description
    if description == '':
        return redirect(url_for("index"))
    if due_date == '':
        date = None
    else:
        date = datetime.strptime(due_date, '%m-%d-%Y')

    new_task = Task(description=description, completed=False, due_date=date)
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/update/<int:id>")
def update(id: int):
    task = Task.query.filter_by(id=id).first()
    task.completed = not task.completed
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete(id: int):
    task = Task.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
