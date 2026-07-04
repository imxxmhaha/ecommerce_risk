export interface Blacklist {
  id: number
  blacklist_type: string
  blacklist_value: string
  remark?: string
  status: number
  deleted: number
  created_at?: string
}
