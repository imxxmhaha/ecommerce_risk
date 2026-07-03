import request from './request'

export function generateAiRule(data: any) {
  return request.post('/api/risk/ai/rules/generate', data)
}

export function explainAiRule(data: any) {
  return request.post('/api/risk/ai/rules/explain', data)
}

export function validateAiRule(data: any) {
  return request.post('/api/risk/ai/rules/validate', data)
}
