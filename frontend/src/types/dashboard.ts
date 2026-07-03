export interface DashboardData {
  event_total: number
  high_risk_rate: number
  case_total: number
  resolved_case_total: number
  avg_case_process_hours: number
  risk_level_distribution: Array<{ name: string; value: number }>
  rule_hit_ranking: Array<{ rule_name: string; rule_code: string; hit_count: number }>
  blacklist_hit_count: number
}
