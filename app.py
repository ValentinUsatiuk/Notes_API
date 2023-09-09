from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

# Налаштування підключення до бази данних
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

# Ініціалізація об'єкта SQLAlchemy
db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run(debug=True)


# Документація API
@app.route("/")
def home():
    return render_template("home.html")


# Отримуємо список усіх заміток
@app.route("/notes", methods=["GET"])
def all_notes():
    result_dict = {}
    return result_dict


# Отримуємо конкретну замітку за id/ новлення існуючої замітки за id/
# Видалення замітки за id
@app.route("/notes/<int:note_id>", methods=["GET", "PUT", "DELETE"])
def note(note_id):
    result_dict = {}
    return result_dict


# Створення нової замітки
@app.route("/methods", methods=["POST"])
def new_notes(title, context):
    result_dict = {}
    return result_dict

