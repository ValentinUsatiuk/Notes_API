from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# Налаштування підключення до бази данних
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

# Ініціалізація об'єкта SQLAlchemy
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nulable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    notes = db.relationship("Note", backref="user",
                            lazy="dynamic", cascade="all, delete-orhan")

    def __repr__(self):
        return '<User %r>' % self.username


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    created_on = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForignKey("user.id"))


# Документація API
@app.route("/")
def home():
    return render_template("home.html")


class AllNotesResource(Resource):
    def get(self):
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

    def post(self):
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
class NoteResource(Resource):
    def get(self, note_id):
        note = self.get_note_by_id(note_id)
        if not note:
            return self.note_not_found_response()

        result_dict = {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_on": note.created_on.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return result_dict

    def put(self, note_id):
        note = self.get_note_by_id(note_id)
        if not note:
            return self.note_not_found_response()

        data = request.get_json()
        if "title" in data:
            note.title = data["title"]
        if "content" in data:
            note.content = data["content"]
        db.session.commit()
        return jsonify({"message": "Note updated successfully"})

    def delete(self, note_id):
        note = self.get_note_by_id(note_id)
        if not note:
            return self.note_not_found_response()

        db.session.delete(note)
        db.session.commit()
        return jsonify({"message": "Note deleted successfully"})

    def get_note_by_id(self, note_id):
        return Note.query.get(note_id)

    def note_not_found_response(self):
        return jsonify({"error": "This note doesn't exist"}), 404


api.add_resource(NoteResource, "/notes/<int:note_id>")
api.add_resource(AllNotesResource, "/notes")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
