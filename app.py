from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:password@localhost/test'
db = SQLAlchemy(app)

# Модели данных для PostgreSQL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(10), unique=True, nullable=False)
    secret = db.Column(db.String(10), nullable=False)
    sessions = db.relationship('Session', backref='user', lazy=True)

class Method(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(30), nullable=False)
    json_params = db.Column(db.JSON, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    sessions = db.relationship('Session', backref='method', lazy=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('method.id'), nullable=False)
    data_in = db.Column(db.String(10000), nullable=False)
    params = db.Column(db.JSON)
    data_out = db.Column(db.String(10000))
    status = db.Column(db.String(20), default='Pending')

# Функция для шифра Виженера
def vigenere_cipher(text, key, decrypt=False):
    alphabet = " ,.:(_)-0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    key_length = len(key)
    key_as_int = [alphabet.index(k) for k in key]
    text_as_int = [alphabet.index(t) for t in text]

    if decrypt:
        key_as_int = [-k for k in key_as_int]

    ciphered = ''
    for i, char in enumerate(text_as_int):
        new_char = (char + key_as_int[i % key_length]) % len(alphabet)
        ciphered += alphabet[new_char]

    return ciphered

# API роуты
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    login = data.get('login')
    secret = data.get('secret')
    if not (login and secret):
        abort(400, 'Both login and secret are required.')
    if len(login) < 3 or len(login) > 10 or len(secret) < 3 or len(secret) > 10:
        abort(400, 'Login and secret must be between 3 and 10 characters.')
    new_user = User(login=login, secret=secret)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully.'}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'login': user.login
        }
        user_list.append(user_data)
    return jsonify({'users': user_list})

@app.route('/methods', methods=['GET'])
def get_methods():
    methods = Method.query.all()
    method_list = []
    for method in methods:
        method_data = {
            'id': method.id,
            'caption': method.caption,
            'json_params': method.json_params,
            'description': method.description
        }
        method_list.append(method_data)
    return jsonify({'methods': method_list})

@app.route('/encrypt', methods=['POST'])
def encrypt_data():
    data = request.get_json()
    method_id = data.get('method_id')
    user_id = data.get('user_id')
    data_in = data.get('data_in')
    params = data.get('params')

    method = Method.query.get(method_id)
    if not method:
        abort(404, 'Method not found.')

    if method.caption == 'Vigenere':
        key = params.get('key')
        encrypted_data = vigenere_cipher(data_in.upper(), key)
    elif method.caption == 'Shift':
        # Implement shift cipher here
        pass
    else:
        abort(400, 'Unsupported encryption method.')

    # Save session
    new_session = Session(
        user_id=user_id,
        method_id=method_id,
        data_in=data_in,
        params=params,
        data_out=encrypted_data,
        status='Encrypted'
    )
    db.session.add(new_session)
    db.session.commit()

    return jsonify({'encrypted_data': encrypted_data}), 200

@app.route('/decrypt', methods=['POST'])
def decrypt_data():
    data = request.get_json()
    session_id = data.get('session_id')
    secret = data.get('secret')

    session = Session.query.get(session_id)
    if not session:
        abort(404, 'Session not found.')
    if session.user.secret != secret:
        abort(401, 'Unauthorized.')

    method = Method.query.get(session.method_id)
    if not method:
        abort(404, 'Method not found.')

    if method.caption == 'Vigenere':
        key = session.params.get('key')
        decrypted_data = vigenere_cipher(session.data_out.upper(), key, decrypt=True)
    elif method.caption == 'Shift':
        # Implement shift cipher decryption here
        pass
    else:
        abort(400, 'Unsupported encryption method.')

    session.status = 'Decrypted'
    db.session.commit()

    return jsonify({'decrypted_data': decrypted_data}), 200

@app.route('/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    session = Session.query.get(session_id)
    if not session:
        abort(404, 'Session not found.')
    session_data = {
        'id': session.id,
        'user_id': session.user_id,
        'method_id': session.method_id,
        'data_in': session.data_in,
        'params': session.params,
        'data_out': session.data_out,
        'status': session.status
    }
    return jsonify({'session': session_data})

@app.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    data = request.get_json()
    secret = data.get('secret')

    session = Session.query.get(session_id)
    if not session:
        abort(404, 'Session not found.')
    if session.user.secret != secret:
        abort(401, 'Unauthorized.')

    db.session.delete(session)
    db.session.commit()

    return jsonify({'message': 'Session deleted successfully.'}), 200

@app.route('/crack', methods=['POST'])
def crack_cipher():
    data = request.get_json()
    session_id = data.get('session_id')

    session = Session.query.get(session_id)
    if not session:
        abort(404, 'Session not found.')

    if session.method.caption == 'Vigenere':
        # Implement Vigenere cipher cracking (frequency analysis, etc.)
        pass
    elif session.method.caption == 'Shift':
        # Implement Shift cipher cracking (brute force, etc.)
        pass
    else:
        abort(400, 'Unsupported encryption method.')

    # For demonstration purposes, return the cracked data (if cracked)
    cracked_data = "Cracked data here"
    return jsonify({'cracked_data': cracked_data}), 200

if __name__ == '__main__':
    app.run(debug=True)
