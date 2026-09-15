from flask import Blueprint, request, jsonify, session

from models.complaint_model import (
    get_all_complaints, get_complaint_by_id, update_complaint_status,
    update_complaint_priority, update_complaint_category, add_status_history,
    get_status_history, get_analytics_summary, VALID_TRANSITIONS
)
from models.notification_model import create_notification
from models.user_model import get_all_users
from services.duplicate_service import check_possible_duplicate
from utils.auth_utils import role_required

admin_bp = Blueprint('admin', __name__)

VALID_CATEGORIES = ['Road', 'Waste', 'Drainage', 'Water', 'Streetlight',
                     'Sanitation', 'Infrastructure', 'Other']
VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Critical']


@admin_bp.route('/api/admin/complaints', methods=['GET'])
@role_required('admin')
def list_all_complaints():
    """
    Supports optional query string filters:
    /api/admin/complaints?status=Submitted&category=Road&priority=High&search=pothole
    """
    status = request.args.get('status')
    category = request.args.get('category')
    priority = request.args.get('priority')
    search = request.args.get('search')

    complaints = get_all_complaints(status=status, category=category, priority=priority, search=search)
    return jsonify({'complaints': complaints}), 200


@admin_bp.route('/api/admin/complaints/<int:complaint_id>', methods=['GET'])
@role_required('admin')
def admin_complaint_detail(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found.'}), 404

    history = get_status_history(complaint_id)
    return jsonify({'complaint': complaint, 'status_history': history}), 200


@admin_bp.route('/api/admin/complaints/<int:complaint_id>/duplicates', methods=['GET'])
@role_required('admin')
def admin_check_duplicates(complaint_id):
    """
    On-demand duplicate check for an EXISTING complaint, run whenever the
    admin opens it to manage it — not just at the moment of submission.
    This lets an admin catch duplicates even if the second report came in
    before the first was verified, or if two citizens report the same
    issue from slightly different accounts/times.
    """
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found.'}), 404

    matches = check_possible_duplicate(
        complaint['category'],
        complaint['description'],
        complaint['latitude'],
        complaint['longitude'],
        exclude_id=complaint_id,
        title=complaint['title']
    )
    return jsonify({'possible_duplicates': matches}), 200


@admin_bp.route('/api/admin/complaints/<int:complaint_id>/status', methods=['PUT'])
@role_required('admin')
def update_status(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found.'}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get('status', '').strip()
    remarks = data.get('remarks', '').strip()

    current_status = complaint['status']
    allowed_next = VALID_TRANSITIONS.get(current_status, [])

    if new_status not in allowed_next:
        return jsonify({
            'error': f"Cannot change status from '{current_status}' to '{new_status}'. "
                     f"Allowed next steps: {', '.join(allowed_next) if allowed_next else 'none (terminal state)'}."
        }), 400

    update_complaint_status(complaint_id, new_status)
    add_status_history(complaint_id, current_status, new_status, session['user_id'], remarks)

    # Notify the citizen who filed the complaint
    create_notification(
        complaint['user_id'],
        complaint_id,
        f"Your complaint \"{complaint['title']}\" is now {new_status}."
    )

    return jsonify({'message': f"Status updated to '{new_status}'."}), 200


@admin_bp.route('/api/admin/complaints/<int:complaint_id>/priority', methods=['PUT'])
@role_required('admin')
def update_priority(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found.'}), 404

    data = request.get_json(silent=True) or {}
    priority = data.get('priority', '').strip()

    if priority not in VALID_PRIORITIES:
        return jsonify({'error': f"Priority must be one of: {', '.join(VALID_PRIORITIES)}"}), 400

    update_complaint_priority(complaint_id, priority)
    return jsonify({'message': f"Priority updated to '{priority}'."}), 200


@admin_bp.route('/api/admin/complaints/<int:complaint_id>/category', methods=['PUT'])
@role_required('admin')
def update_category(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found.'}), 404

    data = request.get_json(silent=True) or {}
    category = data.get('category', '').strip()

    if category not in VALID_CATEGORIES:
        return jsonify({'error': f"Category must be one of: {', '.join(VALID_CATEGORIES)}"}), 400

    update_complaint_category(complaint_id, category)
    return jsonify({'message': f"Category updated to '{category}'."}), 200


@admin_bp.route('/api/admin/analytics', methods=['GET'])
@role_required('admin')
def analytics():
    return jsonify(get_analytics_summary()), 200


@admin_bp.route('/api/admin/users', methods=['GET'])
@role_required('admin')
def list_users():
    """
    Read-only listing of all registered users, with how many complaints
    each has filed. Intentionally does NOT allow changing a user's role
    here — promoting someone to admin is a deliberate, out-of-band action
    (done directly in the database), not a button in the UI, to avoid
    accidental or malicious privilege escalation.
    """
    users = get_all_users()
    return jsonify({'users': users}), 200
