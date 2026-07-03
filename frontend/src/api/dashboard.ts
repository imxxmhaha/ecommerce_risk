import request from './request'

export function getDashboard(params: any) {
  return request.get('/api/risk/dashboard', { params })
}
