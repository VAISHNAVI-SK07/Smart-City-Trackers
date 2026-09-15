from utils.db import get_db_connection

VALID_TRANSITIONS = {
    'Submitted': ['Under Review', 'Rejected'],
    'Under Review': ['Verified', 'Rejected'],
    'Verified': ['In Progress', 'Rejected'],
    'Rejected': [],
    'In Progress': ['Resolved'],
    'Resolved': ['Closed', 'Reopened'],
    'Closed': ['Reopened'],
    'Reopened': ['Under Review', 'In Progress'],
}


def create_complaint(user_id, title, description, category, image_path,
                      latitude, longitude, address, severity, priority):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO complaints
               (user_id, title, description, category, image_path,
                latitude, longitude, address, severity, priority, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Submitted')""",
            (user_id, title, description, category, image_path,
             latitude, longitude, address, severity, priority)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_complaint_by_id(complaint_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT c.*, u.name AS citizen_name, u.email AS citizen_email
               FROM complaints c
               JOIN users u ON c.user_id = u.id
               WHERE c.id = %s""",
            (complaint_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_complaints_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM complaints WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_all_complaints(status=None, category=None, priority=None, search=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """SELECT c.*, u.name AS citizen_name
                   FROM complaints c
                   JOIN users u ON c.user_id = u.id
                   WHERE 1=1"""
        params = []

        if status:
            query += " AND c.status = %s"
            params.append(status)
        if category:
            query += " AND c.category = %s"
            params.append(category)
        if priority:
            query += " AND c.priority = %s"
            params.append(priority)
        if search:
            query += " AND (c.title LIKE %s OR c.description LIKE %s)"
            like_term = f"%{search}%"
            params.extend([like_term, like_term])

        query += " ORDER BY c.created_at DESC"

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def update_complaint_status(complaint_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if new_status == 'Resolved':
            cursor.execute(
                "UPDATE complaints SET status = %s, resolved_at = NOW() WHERE id = %s",
                (new_status, complaint_id)
            )
        else:
            cursor.execute(
                "UPDATE complaints SET status = %s WHERE id = %s",
                (new_status, complaint_id)
            )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def update_complaint_priority(complaint_id, priority):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE complaints SET priority = %s WHERE id = %s",
            (priority, complaint_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def update_complaint_category(complaint_id, category):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE complaints SET category = %s WHERE id = %s",
            (category, complaint_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def add_status_history(complaint_id, old_status, new_status, changed_by, remarks):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO complaint_status_history
               (complaint_id, old_status, new_status, changed_by, remarks)
               VALUES (%s, %s, %s, %s, %s)""",
            (complaint_id, old_status, new_status, changed_by, remarks)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_status_history(complaint_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT h.*, u.name AS changed_by_name
               FROM complaint_status_history h
               JOIN users u ON h.changed_by = u.id
               WHERE h.complaint_id = %s
               ORDER BY h.changed_at ASC""",
            (complaint_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def find_nearby_complaints(category, latitude, longitude, exclude_id=None, radius_degrees=0.003):
    """
    Finds recent, still-open complaints in the same category within a small
    bounding box around the given coordinates (~300m at this radius).

    IMPORTANT: MySQL returns DECIMAL columns as Python's Decimal type, not
    float. Since radius_degrees is a plain float, mixing Decimal and float
    in arithmetic raises a TypeError. We explicitly cast to float here so
    this works regardless of whether the caller passed floats (citizen
    submission form) or Decimals (values re-read from the database, as in
    the admin duplicate-check route).
    """
    latitude = float(latitude)
    longitude = float(longitude)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """SELECT id, title, description, latitude, longitude, status
                   FROM complaints
                   WHERE category = %s
                     AND latitude BETWEEN %s AND %s
                     AND longitude BETWEEN %s AND %s
                     AND status NOT IN ('Rejected', 'Closed')"""
        params = [
            category,
            latitude - radius_degrees, latitude + radius_degrees,
            longitude - radius_degrees, longitude + radius_degrees
        ]
        if exclude_id:
            query += " AND id != %s"
            params.append(exclude_id)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_analytics_summary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        summary = {}

        cursor.execute("SELECT COUNT(*) AS total FROM complaints")
        summary['total_complaints'] = cursor.fetchone()['total']

        cursor.execute(
            "SELECT COUNT(*) AS pending FROM complaints WHERE status IN "
            "('Submitted', 'Under Review', 'Verified', 'In Progress', 'Reopened')"
        )
        summary['pending_complaints'] = cursor.fetchone()['pending']

        cursor.execute(
            "SELECT COUNT(*) AS resolved FROM complaints WHERE status IN ('Resolved', 'Closed')"
        )
        summary['resolved_complaints'] = cursor.fetchone()['resolved']

        cursor.execute("SELECT COUNT(*) AS critical FROM complaints WHERE priority = 'Critical'")
        summary['critical_complaints'] = cursor.fetchone()['critical']

        cursor.execute(
            "SELECT category, COUNT(*) AS count FROM complaints GROUP BY category ORDER BY count DESC"
        )
        summary['by_category'] = cursor.fetchall()

        cursor.execute(
            "SELECT status, COUNT(*) AS count FROM complaints GROUP BY status"
        )
        summary['by_status'] = cursor.fetchall()

        cursor.execute(
            """SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(*) AS count
               FROM complaints GROUP BY month ORDER BY month ASC"""
        )
        summary['by_month'] = cursor.fetchall()

        cursor.execute(
            """SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, resolved_at)) AS avg_hours
               FROM complaints WHERE resolved_at IS NOT NULL"""
        )
        row = cursor.fetchone()
        summary['avg_resolution_hours'] = round(row['avg_hours'], 1) if row['avg_hours'] else None

        return summary
    finally:
        cursor.close()
        conn.close()
