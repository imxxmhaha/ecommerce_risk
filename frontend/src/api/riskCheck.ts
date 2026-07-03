import request from './request'

export function checkRisk(data: any) {
  return request.post('/api/risk/check', data)
}
