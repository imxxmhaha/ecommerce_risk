export interface RuleHit {
  rule_code: string
  rule_name: string
  priority?: number
  hit_score: number
  is_effective?: boolean
  hit_message?: string
}

export interface RiskCheckResult {
  assessment_id: number
  event_id: number
  risk_score: number
  risk_level: string
  decision: string
  case_id?: number
  rule_hits: RuleHit[]
  feature_snapshot: Record<string, unknown>
}
