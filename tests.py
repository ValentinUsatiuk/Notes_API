import requests

# URL for testing
BASE_URL = 'http://127.0.0.1:5000'


# New user registration test
def test_registration():
    response = requests.post(BASE_URL + '/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    assert response.json() == {'message': 'User registered successfully'}


# User registration test with the same name (must be deleted)
def test_duplicate_registration():
    response = requests.post(BASE_URL + '/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 400
    assert response.json() == {
        'message': 'User with this username already exists'}


# User authorization test
def test_login():
    response = requests.post(BASE_URL + '/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert response.json() == {'message': 'Login successfully'}


# User authorization test with incorrect password
def test_invalid_login():
    response = requests.post(BASE_URL + '/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json() == {'message': 'Invalid username or password'}


# Test of creating a new note
def test_create_note():
    response = requests.post(BASE_URL + '/notes', json={
        'title': 'Test Note',
        'content': 'This is a test note',
        'user_id': 1
        # The user ID you registered earlier
    })
    assert response.status_code == 200
    assert response.json() == {'message': 'The note was created successfully'}


# Test for obtaining a list of all notes
def test_get_all_notes():
    response = requests.get(BASE_URL + '/notes')
    assert response.status_code == 200
    # Checking if a list of notes was received in the response
    assert 'notes' in response.json()


# A test of obtaining information about a specific note
def test_get_note_by_id():
    response = requests.get(
        BASE_URL + '/notes/1')  # 1 - is the ID of the previously created note
    assert response.status_code == 200
    # Checking if the note information was received in the response
    assert 'title' in response.json()
    assert 'content' in response.json()


# Note update test
def test_update_note():
    response = requests.put(BASE_URL + '/notes/1', json={
        'title': 'Updated Note',
        'content': 'This note has been updated'
    })
    assert response.status_code == 200
    assert response.json() == {'message': 'Note updated successfully'}


# Note deletion test
def test_delete_note():
    response = requests.delete(
        BASE_URL + '/notes/1')  # Let's delete the note we created earlier
    assert response.status_code == 200
    assert response.json() == {'message': 'Note deleted successfully'}


if __name__ == '__main__':
    # Running tests
    test_registration()
    test_duplicate_registration()
    test_login()
    test_invalid_login()
    test_create_note()
    test_get_all_notes()
    test_get_note_by_id()
    test_update_note()
    test_delete_note()
    print('All tests passed!')
