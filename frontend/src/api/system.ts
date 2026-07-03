import request from './request'

export function listSystemUsers(params?: Record<string, any>) {
  return request.get('/api/system/users', { params })
}

export function createSystemUser(data: { username: string; password: string; real_name: string; role_codes: string[]; status?: string }) {
  return request.post('/api/system/users', data)
}

export function setSystemUserStatus(data: { user_id: number; status: string }) {
  return request.post('/api/system/users/status', data)
}

export function resetSystemUserPassword(data: { user_id: number; password: string }) {
  return request.post('/api/system/users/password', data)
}

export function listSystemRoles() {
  return request.get('/api/system/roles')
}

export function listSystemPermissions() {
  return request.get('/api/system/permissions')
}
