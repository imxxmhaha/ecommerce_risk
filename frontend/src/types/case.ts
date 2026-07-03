export interface RiskCase {
  id: number
  assessment_id: number
  user_id: string
  order_id?: string
  case_status: string
  reviewer_id?: string
  review_result?: string
  review_remark?: string
  created_at?: string
}
