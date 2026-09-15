from flask import Blueprint, jsonify, session

from models.notification_model import get_notifications_by_user, mark_notification_read
from utils.auth_utils import login_required

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('/api/notifications', methods=['GET'])
@login_required
def list_notifications():
    notifications = get_notifications_by_user(session['user_id'])
    return jsonify({'notifications': notifications}), 200


@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@login_required
def mark_read(notification_id):
    success = mark_notification_read(notification_id, session['user_id'])
    if not success:
        return jsonify({'error': 'Notification not found.'}), 404
    return jsonify({'message': 'Notification marked as read.'}), 200
