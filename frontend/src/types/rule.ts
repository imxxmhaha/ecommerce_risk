export interface RiskRule {
  id?: number
  rule_code: string
  rule_name: string
  rule_status: number
  priority: number
  score: number
  condition_json: Record<string, unknown>
  description?: string
  hit_count?: number
}
