from flask import Blueprint, request, jsonify, session

from models.complaint_model import (
    create_complaint, get_complaint_by_id, get_complaints_by_user,
    update_complaint_status, add_status_history, get_status_history,
    VALID_TRANSITIONS
)
from models.feedback_model import create_feedback, get_feedback_by_complaint
from services.priority_service import recommend_priority
from services.duplicate_service import check_possible_duplicate
from utils.auth_utils import login_required
from utils.validators import is_non_empty_string, is_valid_coordinate
from utils.file_utils import save_uploaded_image

citizen_bp = Blueprint('citizen', __name__)

VALID_CATEGORIES = ['Road', 'Waste', 'Drainage', 'Water', 'Streetlight',
                     'Sanitation', 'Infrastructure', 'Other']
VALID_SEVERITIES = ['Low', 'Medium', 'High', 'Critical']


@citizen_bp.route('/api/complaints', methods=['POST'])
@login_required
def submit_complaint():
    """
    Submits a new complaint. Uses multipart/form-data (not JSON) because
    it includes an image file upload alongside text fields.
    """
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()
    severity = request.form.get('severity', 'Medium').strip()
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    address = request.form.get('address', '').strip()

    # --- Validation ---
    if not is_non_empty_string(title, min_length=5, max_length=150):
        return jsonify({'error': 'Title must be between 5 and 150 characters.'}), 400
    if not is_non_empty_string(description, min_length=15):
        return jsonify({'error': 'Description must be at least 15 characters.'}), 400
    if category not in VALID_CATEGORIES:
        return jsonify({'error': f"Category must be one of: {', '.join(VALID_CATEGORIES)}"}), 400
    if severity not in VALID_SEVERITIES:
        return jsonify({'error': f"Severity must be one of: {', '.join(VALID_SEVERITIES)}"}), 400

    lat_val = lng_val = None
    if latitude and longitude:
        if not is_valid_coordinate(latitude, longitude):
            return jsonify({'error': 'Invalid latitude/longitude values.'}), 400
        lat_val, lng_val = float(latitude), float(longitude)

    # --- Image upload ---
    image_path = None
    if 'image' in request.files:
        try:
            image_path = save_uploaded_image(request.files['image'])
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    # --- Smart features: priority recommendation + duplicate check ---
    priority = recommend_priority(category, severity)
    duplicate_warnings = check_possible_duplicate(
        category, description, lat_val, lng_val, title=title
    )

    user_id = session['user_id']
    complaint_id = create_complaint(
        user_id, title, description, category, image_path,
        lat_val, lng_val, address, severity, priority
    )

    add_status_history(complaint_id, None, 'Submitted', user_id, 'Complaint submitted by citizen.')

    response = {
        'message': 'Complaint submitted successfully.',
        'complaint_id': complaint_id,
        'recommended_priority': priority
    }
    if duplicate_warnings:
        response['duplicate_warning'] = (
            'Possible duplicate complaint detected nearby. Admin will review.'
        )
        response['possible_duplicates'] = duplicate_warnings

    return jsonify(response), 201


@citizen_bp.route('/api/complaints/my', methods=['GET'])
@login_required
def my_complaints():
    complaints = get_complaints_by_user(session['user_id'])
    return jsonify({'complaints': complaints}), 200


@citizen_bp.route('/api/complaints/<int:complaint_id>', methods=['GET'])
@login_required
def complaint_detail(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found.'}), 404

    if session['role'] != 'admin' and complaint['user_id'] != session['user_id']:
        return jsonify({'error': 'You do not have permission to view this complaint.'}), 403

    history = get_status_history(complaint_id)
    feedback = get_feedback_by_complaint(complaint_id)

    return jsonify({
        'complaint': complaint,
        'status_history': history,
        'feedback': feedback
    }), 200


@citizen_bp.route('/api/complaints/<int:complaint_id>/reopen', methods=['PUT'])
@login_required
def reopen_complaint(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found.'}), 404
    if complaint['user_id'] != session['user_id']:
        return jsonify({'error': 'You can only reopen your own complaints.'}), 403

    current_status = complaint['status']
    if 'Reopened' not in VALID_TRANSITIONS.get(current_status, []):
        return jsonify({
            'error': f"A complaint with status '{current_status}' cannot be reopened."
        }), 400

    data = request.get_json(silent=True) or {}
    remarks = data.get('remarks', 'Citizen reported the issue is not actually resolved.')

    update_complaint_status(complaint_id, 'Reopened')
    add_status_history(complaint_id, current_status, 'Reopened', session['user_id'], remarks)

    return jsonify({'message': 'Complaint reopened.'}), 200


@citizen_bp.route('/api/complaints/<int:complaint_id>/feedback', methods=['POST'])
@login_required
def submit_feedback(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found.'}), 404
    if complaint['user_id'] != session['user_id']:
        return jsonify({'error': 'You can only give feedback on your own complaints.'}), 403
    if complaint['status'] not in ('Resolved', 'Closed'):
        return jsonify({'error': 'Feedback can only be given after a complaint is resolved.'}), 400
    if get_feedback_by_complaint(complaint_id):
        return jsonify({'error': 'Feedback has already been submitted for this complaint.'}), 409

    data = request.get_json(silent=True) or {}
    rating = data.get('rating')
    comment = data.get('comment', '').strip()

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({'error': 'Rating must be a number between 1 and 5.'}), 400
    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5.'}), 400

    feedback_id = create_feedback(complaint_id, session['user_id'], rating, comment)
    return jsonify({'message': 'Feedback submitted. Thank you!', 'feedback_id': feedback_id}), 201
