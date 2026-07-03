<template>
  <div class="page">
    <div class="page-title"><h2>用户画像</h2></div>
    <div class="panel toolbar">
      <el-input v-model="userId" placeholder="用户编号" style="width: 240px" />
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    <div v-if="profile" class="metric-grid">
      <div class="metric"><div class="metric-label">事件总数</div><div class="metric-value">{{ profile.summary.event_count }}</div></div>
      <div class="metric"><div class="metric-label">高风险次数</div><div class="metric-value">{{ profile.summary.high_risk_count }}</div></div>
      <div class="metric"><div class="metric-label">案件数</div><div class="metric-value">{{ profile.summary.case_count }}</div></div>
      <div class="metric"><div class="metric-label">拒绝次数</div><div class="metric-value">{{ profile.summary.reject_count }}</div></div>
    </div>
    <div v-if="profile" class="two-col">
      <div class="panel"><h3>最近事件</h3><el-table :data="profile.recent_events" border size="small"><el-table-column prop="event_type" label="事件" /><el-table-column prop="order_id" label="订单" /><el-table-column prop="created_at" label="时间" /></el-table></div>
      <div class="panel"><h3>常命中规则</h3><el-table :data="profile.top_hit_rules" border size="small"><el-table-column prop="rule_name" label="规则" /><el-table-column prop="rule_code" label="编码" /><el-table-column prop="hit_count" label="次数" /></el-table></div>
    </div>
    <div v-if="profile" class="panel"><h3>关联案件</h3><el-table :data="profile.related_cases" border><el-table-column prop="id" label="案件" /><el-table-column prop="order_id" label="订单" /><el-table-column label="状态"><template #default="{ row }"><CaseStatusTag :status="row.case_status" /></template></el-table-column><el-table-column prop="created_at" label="时间" /></el-table></div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CaseStatusTag from '../components/CaseStatusTag.vue'
import { getUserProfile } from '../api/profile'

const userId = ref('U10001')
const profile = ref<any>(null)
async function load() { profile.value = await getUserProfile(userId.value) }
</script>
