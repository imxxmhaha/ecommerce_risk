import request from './request'

export function listBlacklists(params: any) {
  return request.get('/api/risk/blacklists', { params })
}

export function createBlacklist(data: any) {
  return request.post('/api/risk/blacklists', data)
}

export function deleteBlacklist(data: any) {
  return request.post('/api/risk/blacklists/delete', data)
}
