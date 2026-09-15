/* ============================================================
   SMART CIVIC TRACKER — API HELPER
   ============================================================ */

const API_BASE = 'http://127.0.0.1:5000';

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...options,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (e) {}

  if (!response.ok) {
    const message = (data && data.error) ? data.error : `Request failed (${response.status})`;
    throw new Error(message);
  }

  return data;
}

function apiJson(path, method, body) {
  return apiRequest(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

const Api = {
  register: (payload) => apiJson('/api/register', 'POST', payload),
  login: (payload) => apiJson('/api/login', 'POST', payload),
  logout: () => apiRequest('/api/logout', { method: 'POST' }),
  me: () => apiRequest('/api/me'),
  getProfile: () => apiRequest('/api/profile'),
  updateProfile: (payload) => apiJson('/api/profile', 'PUT', payload),

  submitComplaint: (formData) => apiRequest('/api/complaints', {
    method: 'POST',
    body: formData,
  }),
  myComplaints: () => apiRequest('/api/complaints/my'),
  complaintDetail: (id) => apiRequest(`/api/complaints/${id}`),
  reopenComplaint: (id, remarks) => apiJson(`/api/complaints/${id}/reopen`, 'PUT', { remarks }),
  submitFeedback: (id, rating, comment) => apiJson(`/api/complaints/${id}/feedback`, 'POST', { rating, comment }),

  notifications: () => apiRequest('/api/notifications'),
  markNotificationRead: (id) => apiRequest(`/api/notifications/${id}/read`, { method: 'PUT' }),

  adminComplaints: (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    return apiRequest(`/api/admin/complaints${params ? '?' + params : ''}`);
  },
  adminComplaintDetail: (id) => apiRequest(`/api/admin/complaints/${id}`),
  checkDuplicates: (id) => apiRequest(`/api/admin/complaints/${id}/duplicates`),
  updateStatus: (id, status, remarks) => apiJson(`/api/admin/complaints/${id}/status`, 'PUT', { status, remarks }),
  updatePriority: (id, priority) => apiJson(`/api/admin/complaints/${id}/priority`, 'PUT', { priority }),
  updateCategory: (id, category) => apiJson(`/api/admin/complaints/${id}/category`, 'PUT', { category }),
  analytics: () => apiRequest('/api/admin/analytics'),
  adminUsers: () => apiRequest('/api/admin/users'),
};

function imageUrl(imagePath) {
  if (!imagePath) return null;
  return `${API_BASE}/${imagePath}`;
}

function statusClass(status) {
  return status.replace(/\s+/g, '-');
}

function formatDate(dateString) {
  if (!dateString) return '';
  const d = new Date(dateString);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) +
         ' · ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

async function requireAuth(requiredRole = null) {
  try {
    const result = await Api.me();
    if (!result.logged_in) {
      window.location.href = 'login.html';
      return null;
    }
    if (requiredRole && result.user.role !== requiredRole) {
      window.location.href = result.user.role === 'admin' ? 'admin-dashboard.html' : 'citizen-dashboard.html';
      return null;
    }
    return result.user;
  } catch (e) {
    window.location.href = 'login.html';
    return null;
  }
}

function showAlert(containerId, message, type = 'danger') {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
}
