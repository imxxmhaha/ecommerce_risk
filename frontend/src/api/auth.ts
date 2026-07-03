import request from './request'

export function login(data: { username: string; password: string }) {
  return request.post('/api/auth/login', data)
}

export function getMe() {
  return request.get('/api/auth/me')
}

export function bootstrapAdmin(data: { bootstrap_token: string; username: string; password: string; real_name: string }) {
  return request.post('/api/auth/bootstrap-admin', data)
}
