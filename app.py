from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
api = Api(app)

# Database connection settings
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)


class User(db.Model):
    """
    A user model representing the user table in the database.

    Attributes:
        id (int): Unique user ID.
        username (str): Unique username.
        password_hash (str): A hash of the user's password.
        notes (relationship): Relation to user notes.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    notes = db.relationship("Note", backref="user",
                            lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return '<User %r>' % self.username


class Note(db.Model):
    """
    A note model that represents a table of notes in the database.

    Attributes:
        id (int): The unique identifier of the note.
        title (str): The title of the note.
        content (str): Content of the note.
        created_on (datetime): The date and time the note was created.
        user_id (int): The ID of the user who owns the note.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    created_on = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


# Документація API
@app.route("/")
def home():
    return render_template("home.html")


class AllNotesResource(Resource):
    """
    A class that represents a resource for getting a list of all notes.

    Methods:
        get(): Get a list of all notes.
        post(): Create a new note.
    """
    def get(self):
        all_notes = Note.query.all()
        notes_list = []
        for note in all_notes:
            note_data = {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_on": note.created_on.strftime('%Y-%m-%d %H:%M:%S'),
                "user_id": note.user_id,
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
            user_id=data["user_id"],
        )
        db.session.add(new_note)
        db.session.commit()
        return jsonify({'message': 'The note was created successfully'})


class NoteResource(Resource):
    """
    A class that represents a resource for operations with a single note.

    Methods:
        get(note_id): Get information about a note with the specified ID.
        put(note_id): Update the note with the specified ID.
        delete(note_id): Delete the note with the specified ID.
    """
    def get(self, note_id):
        note = self.get_note_by_id(note_id)
        if not note:
            return self.note_not_found_response(note_id)

        result_dict = {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_on": note.created_on.strftime('%Y-%m-%d %H:%M:%S'),
            "user_id": note.user_id,
        }
        return result_dict

    def put(self, note_id):
        note = self.get_note_by_id(note_id)
        if not note:
            return self.note_not_found_response(note_id)

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
            return self.note_not_found_response(note_id)

        db.session.delete(note)
        db.session.commit()
        return jsonify({"message": "Note deleted successfully"})

    def get_note_by_id(self, note_id):
        note = Note.query.get(note_id)
        if not note:
            return None
        return note

    def note_not_found_response(self, note_id):
        if note_id is not None:
            return {
                "error": "Note with ID {} doesn't exist".format(note_id)}, 404
        else:
            return {"error": "No note ID provided"}, 400


# checking the request for username and password
def parse_user_args():
    user_parser = reqparse.RequestParser()
    user_parser.add_argument("username", type=str, required=True,
                             help="Username is required")
    user_parser.add_argument("password", type=str, required=True,
                             help="Password is required")
    args = user_parser.parse_args()
    username = args['username']
    password = args['password']

    return username, password


class RegisterResource(Resource):
    """
    A class that represents a resource for registering new users.

    Methods:
        post(): Register a new user.
    """
    def post(self):
        username, password = parse_user_args()

        # Checking if a user with that name already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {"message": 'User with this username already exists'}, 400

        # Create a new user
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201


class LoginResource(Resource):
    """
    A class that represents a resource for user authorization.

    Methods:
        post(): Authorize the user.
    """
    def post(self):
        username, password = parse_user_args()

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            return {'message': 'Login successfully'}
        else:
            return {'message': 'Invalid username or password'}, 401


api.add_resource(RegisterResource, '/register')
api.add_resource(LoginResource, '/login')
api.add_resource(NoteResource, "/notes/<int:note_id>")
api.add_resource(AllNotesResource, "/notes")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=False)

