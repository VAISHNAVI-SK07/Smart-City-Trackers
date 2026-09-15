from flask import Blueprint, request, jsonify, session
from models.user_model import create_user, get_user_by_email
from utils.auth_utils import hash_password, verify_password
from utils.validators import is_valid_email, is_valid_password, is_non_empty_string

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/register', methods=['POST'])
def register():
    """
    Creates a new CITIZEN account.
    Note: role is never read from the request — it's hardcoded to 'citizen'
    below, so nobody can register themselves as an admin via this API.
    """
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    address = data.get('address', '').strip()

    if not is_non_empty_string(name, min_length=2, max_length=100):
        return jsonify({'error': 'Name must be between 2 and 100 characters.'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Please provide a valid email address.'}), 400
    if not is_valid_password(password):
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    if get_user_by_email(email):
        return jsonify({'error': 'An account with this email already exists.'}), 409

    password_hash = hash_password(password)
    user_id = create_user(name, email, phone, password_hash, 'citizen', address)

    return jsonify({
        'message': 'Registration successful. You can now log in.',
        'user_id': user_id
    }), 201


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    user = get_user_by_email(email)
    if not user or not verify_password(password, user['password_hash']):
        return jsonify({'error': 'Invalid email or password.'}), 401

    # The session is the SINGLE source of truth for who's logged in and
    # what role they have. The frontend can never override this.
    session['user_id'] = user['id']
    session['role'] = user['role']
    session['name'] = user['name']

    return jsonify({
        'message': 'Login successful.',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully.'}), 200


@auth_bp.route('/api/me', methods=['GET'])
def me():
    """Lets the frontend ask 'am I logged in, and as whom?' on page load."""
    if 'user_id' not in session:
        return jsonify({'logged_in': False}), 200

    return jsonify({
        'logged_in': True,
        'user': {
            'id': session['user_id'],
            'name': session['name'],
            'role': session['role']
        }
    }), 200
