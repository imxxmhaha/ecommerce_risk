import request from './request'

export function listCases(params: any) {
  return request.get('/api/risk/cases', { params })
}

export function getCaseDetail(id: number | string) {
  return request.get(`/api/risk/cases/${id}`)
}

export function reviewCase(data: any) {
  return request.post('/api/risk/cases/review', data)
}
