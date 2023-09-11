from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Налаштування підключення до бази данних
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

# Ініціалізація об'єкта SQLAlchemy
db = SQLAlchemy(app)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    created_on = db.Column(db.Date)


# Документація API
@app.route("/")
def home():
    return render_template("home.html")


# Отримуємо список усіх заміток
@app.route("/notes", methods=["GET", "POST"])
def all_notes():
    if request.method == "GET":
        all_notes = Note.query.all()
        notes_list = []
        for note in all_notes:
            note_data = {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_on": note.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            }
            notes_list.append(note_data)
        return jsonify(notes=notes_list)
    if request.method == "POST":
        data = request.get_json()
        if "title" not in data or "content" not in data:
            return jsonify({"error": 'Insufficient data to create note'})
        new_note = Note(
            title=data["title"],
            content=data["content"],
            created_on=datetime.utcnow(),
        )
        db.session.add(new_note)
        db.session.commit()
        return jsonify({'message': 'The note was created successfully'})

# Отримуємо конкретну замітку за id/ новлення існуючої замітки за id/
# Видалення замітки за id
@app.route("/notes/<int:note_id>", methods=["GET", "PUT", "DELETE"])
def note(note_id):
    note = Note.query.get(note_id)
    if note:
        if request.method == "GET":
            result_dict = {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_on": note.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            }
            return result_dict
        if request.method == "PUT":
            data = request.get_json()
            if note is None:
                return jsonify({'error': "This note doesn't exist"}), 404
            if "title: in data":
                note.title = data["title"]
            if "content" in data:
                note.content = data["content"]
            db.session.commit()
            return jsonify({"message": "Note updated successfully"})
        if request.method == "DELETE":
            if note is None:
                return jsonify({'error': "This note doesn't exist"}), 404
            db.session.delete(note)
            db.session.commit()
            return jsonify({"message": "Note delete successfully"})
    else:
        return jsonify({"error": "This note doesn't exist"}, 404)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
