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

export function analyzeRuleOverlap(data: any) {
  return request.post('/api/risk/ai/rules/overlap', data)
}

export function generateRuleTestCases(data: any) {
  return request.post('/api/risk/ai/rules/test-cases', data)
}

export function explainRiskCase(data: any) {
  return request.post('/api/risk/ai/rules/case-explain', data)
}

export function analyzeDashboardTrend(data: any) {
  return request.post('/api/risk/ai/rules/dashboard-analyze', data)
}
