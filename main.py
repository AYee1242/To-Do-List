from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_bootstrap import Bootstrap
from datetime import datetime
from forms import RegisterForm, LoginForm


app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
bootstrap = Bootstrap(app)

# Setting up app to work with sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "tasks" refers to the tasks protperty in the User class.
    user = relationship("User", back_populates="tasks")

    description = db.Column(db.String(250), unique=False, nullable=False)
    completed = db.Column(db.Boolean, unique=False, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    # This will act like a List of Task objects attached to each User.
    # The "user" refers to the user property in the BlogPost class.
    tasks = relationship("Task", back_populates="user")


@app.route("/todo")
def index():
    if current_user.is_authenticated:
        todo_list = Task.query.filter_by(user=current_user).order_by(Task.due_date).all()
        return render_template("index.html", todo_list=todo_list)
    else:
        return redirect(url_for("sign_in"))


@app.route("/", methods=["GET", "POST"])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            form.email.errors.append("The email does not exist. Please try again.")
            return render_template("signin.html", form=form, current_user=current_user)

        if not check_password_hash(user.password, password):
            form.password.errors.append("Password is incorrect. Please try again")
            return render_template("signin.html", form=form, current_user=current_user)
        login_user(user)
        return redirect(url_for("index"))
    
    return render_template("signin.html", form=form, current_user=current_user)

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    form = RegisterForm()

    if form.validate_on_submit():

        # If user's email already exists
        if User.query.filter_by(email=form.email.data).first():
            # Send flash messsage
            form.email.errors.append("You've already signed up with that email, log in instead!")
            # Redirect to /login route.
            return render_template("signup.html", form=form, current_user=current_user)

        hashed_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8)

        user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data
        )

        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("index"))
    return render_template("signup.html", form=form, current_user=current_user)

@app.route("/signout", methods=["POST"])
def sign_out():
    logout_user()
    return redirect(url_for("sign_in"))

@app.route("/dummyaccount")
def dummy_sign_in():
    user = User.query.filter_by(email="test123@gmail.com").first()
    login_user(user)
    return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add():
    description = request.form.get("description")
    due_date = request.form.get("due_date")

    # Dont add task if there is no description
    if description == "":
        return redirect(url_for("index"))
    if due_date == "":
        date = None
    else:
        date = datetime.strptime(due_date, "%m-%d-%Y")

    new_task = Task(description=description, completed=False,  user=current_user, due_date=date)
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
