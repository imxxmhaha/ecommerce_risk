import request from './request'

export function getUserProfile(userId: string) {
  return request.get(`/api/risk/users/${userId}/profile`)
}
