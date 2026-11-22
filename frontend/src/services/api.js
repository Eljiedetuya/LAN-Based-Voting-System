/** Same-origin API client. The browser stores only Django's HttpOnly session cookie. */
export class ApiError extends Error {
  constructor(message, status = 0, code = 'request_failed', details = null) {
    super(message); this.name = 'ApiError'; this.status = status; this.code = code; this.details = details
  }
}
const readCookie = name => document.cookie.split('; ').find(c => c.startsWith(`${name}=`))?.slice(name.length + 1) || ''
const flatten = value => {
  if (typeof value === 'string') return value
  if (Array.isArray(value)) return value.map(flatten).join('; ')
  if (value && typeof value === 'object') return Object.entries(value).map(([k,v]) => `${k}: ${flatten(v)}`).join('; ')
  return 'Request failed.'
}
export async function request(path, {method = 'GET', data, signal} = {}) {
  const unsafe = !['GET', 'HEAD', 'OPTIONS'].includes(method.toUpperCase())
  const headers = {'Accept': 'application/json'}
  const isFormData = typeof FormData !== 'undefined' && data instanceof FormData
  if (data !== undefined && !isFormData) headers['Content-Type'] = 'application/json'
  if (unsafe) {
    const csrf = readCookie('csrftoken')
    if (!csrf) throw new ApiError('CSRF token is missing. Refresh the page and sign in again.', 403, 'csrf_missing')
    headers['X-CSRFToken'] = decodeURIComponent(csrf)
  }
  let response
  try {
    response = await fetch(path.startsWith('/api/') ? path : `/api/${path.replace(/^\//, '')}`, {
      method, headers, credentials: 'same-origin', body: data === undefined ? undefined : (isFormData ? data : JSON.stringify(data)), signal,
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new ApiError('Cannot reach the local election server. Check your LAN connection. A pending ballot may still have been recorded.', 0, 'network_unavailable')
  }
  const raw = await response.text()
  let parsed = null
  if (raw) {
    try { parsed = JSON.parse(raw) } catch { throw new ApiError('Unexpected server response. Please contact the election administrator.', response.status, 'invalid_json') }
  }
  if (!response.ok) {
    if ((response.status === 401 || response.status === 403) && !path.includes('/auth/')) {
      try {
        const sessionCheck = await fetch('/api/auth/me/', {credentials:'same-origin', headers:{Accept:'application/json'}})
        if (!sessionCheck.ok && (sessionCheck.status===401 || sessionCheck.status===403)) {
          window.dispatchEvent(new Event('campusvote-session-expired'))
        }
      } catch { /* Network failure is not proof of session expiration. */ }
    }
    const detail = parsed?.error?.detail ?? parsed?.detail ?? parsed
    throw new ApiError(flatten(detail) || `Request failed (HTTP ${response.status}).`, response.status, parsed?.error?.code || parsed?.code || `http_${response.status}`, detail)
  }
  return parsed
}
export const api = {
  csrf: () => request('/api/auth/csrf/'),
  login: (username, password) => request('/api/auth/login/', {method:'POST', data:{username,password}}),
  logout: () => request('/api/auth/logout/', {method:'POST'}),
  me: () => request('/api/auth/me/'),
  changePassword: (current_password, new_password) => request('/api/auth/password/change/', {method:'POST', data:{current_password,new_password}}),
  activeElections: () => request('/api/elections/active/'),
  candidates: id => request(`/api/elections/${id}/candidates/`),
  myStatus: id => request(`/api/elections/${id}/my-status/`),
  submitVote: (id, selections) => request(`/api/elections/${id}/submit-vote/`, {method:'POST', data:{selections}}),
  elections: () => request('/api/admin/elections/'),
  election: id => request(`/api/admin/elections/${id}/`),
  createElection: data => request('/api/admin/elections/', {method:'POST',data}),
  updateElection: (id,data) => request(`/api/admin/elections/${id}/`,{method:'PATCH',data}),
  changeElection: (id,action) => request(`/api/admin/elections/${id}/${action}/`,{method:'POST'}),
  positions: id => request(`/api/admin/elections/${id}/positions/`),
  createPosition: (id,data) => request(`/api/admin/elections/${id}/positions/`,{method:'POST',data}),
  candidatesAdmin: id => request(`/api/admin/candidates/${id ? `?election_id=${encodeURIComponent(id)}` : ''}`),
  createCandidate: data => request('/api/admin/candidates/',{method:'POST',data}),
  updateCandidate: (id,data) => request(`/api/admin/candidates/${id}/`,{method:'PATCH',data}),
  voters: (search='',includeInactive=false) => request(`/api/admin/voters/?page_size=100${search ? `&search=${encodeURIComponent(search)}` : ''}${includeInactive?'&include_inactive=true':''}`),
  voter: id => request(`/api/admin/voters/${id}/`),
  createVoter: data => request('/api/admin/voters/',{method:'POST',data}),
  updateVoter: (id,data) => request(`/api/admin/voters/${id}/`,{method:'PATCH',data}),
  staff: () => request('/api/admin/staff/'),
  createStaff: data => request('/api/admin/staff/',{method:'POST',data}),
  eligibility: id => request(`/api/admin/elections/${id}/eligibility/`),
  addEligibility: (id,user_id) => request(`/api/admin/elections/${id}/eligibility/`,{method:'POST',data:{user_id}}),
  previewBulkEligibility: (id,data) => request(`/api/admin/elections/${id}/eligibility/bulk/preview/`,{method:'POST',data}),
  assignBulkEligibility: (id,data) => request(`/api/admin/elections/${id}/eligibility/bulk/`,{method:'POST',data}),
  removeEligibility: (id,user_id) => request(`/api/admin/elections/${id}/eligibility/`,{method:'DELETE',data:{user_id}}),
  monitorElections: () => request('/api/monitoring/elections/'),
  participation: id => request(`/api/monitoring/participation/?election_id=${encodeURIComponent(id)}`),
  health: () => request('/api/monitoring/health/'),
  publicHealth: () => request('/api/health/'),
  results: id => request(`/api/results/${id}/`),
  integrity: id => request(`/api/monitoring/integrity/${id}/`),
  reportCsvUrl: id => `/api/reports/${encodeURIComponent(id)}/csv/`,
  audit: () => request('/api/admin/audit-events/'),
}
export async function checkHealth(signal) {
  const data = await request('/api/health/',{signal})
  return data?.status === 'ok' ? 'healthy' : 'unavailable'
}
