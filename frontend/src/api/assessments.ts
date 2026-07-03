import request from './request'

export function getAssessment(id: number | string) {
  return request.get(`/api/risk/assessments/${id}`)
}
