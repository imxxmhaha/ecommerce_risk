import request from './request'

export function listRules(params: any) {
  return request.get('/api/risk/rules', { params })
}

export function createRule(data: any) {
  return request.post('/api/risk/rules', data)
}

export function updateRule(data: any) {
  return request.post('/api/risk/rules/update', data)
}

export function setRuleStatus(data: any) {
  return request.post('/api/risk/rules/status', data)
}

export function deleteRule(data: any) {
  return request.post('/api/risk/rules/delete', data)
}
