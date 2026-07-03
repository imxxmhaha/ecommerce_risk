<template>
  <div class="page">
    <div class="page-title"><h2>风险检查</h2></div>
    <div class="panel">
      <el-form :model="form" label-width="90px">
        <div class="two-col">
          <el-form-item label="事件类型"><el-select v-model="form.event_type"><el-option v-for="x in eventTypes" :key="x" :label="x" :value="x" /></el-select></el-form-item>
          <el-form-item label="来源编号"><el-input v-model="form.source_id" /></el-form-item>
          <el-form-item label="用户编号"><el-input v-model="form.user_id" /></el-form-item>
          <el-form-item label="订单编号"><el-input v-model="form.order_id" /></el-form-item>
        </div>
        <el-form-item label="事件参数"><JsonEditor v-model="form.event_payload" :rows="10" /></el-form-item>
        <el-form-item><el-button type="primary" :loading="loading" @click="submit">发起风险检查</el-button></el-form-item>
      </el-form>
    </div>
    <div v-if="result" class="metric-grid">
      <div class="metric"><div class="metric-label">风险评分</div><div class="metric-value">{{ result.risk_score }}</div></div>
      <div class="metric"><div class="metric-label">风险等级</div><div class="metric-value"><RiskLevelTag :level="result.risk_level" /></div></div>
      <div class="metric"><div class="metric-label">处理建议</div><div class="metric-value">{{ result.decision }}</div></div>
      <div class="metric"><div class="metric-label">案件编号</div><div class="metric-value">{{ result.case_id || '-' }}</div></div>
    </div>
    <div v-if="result" class="two-col">
      <div class="panel"><h3>命中规则</h3><RuleHitList :items="result.rule_hits" /></div>
      <div class="panel"><h3>特征快照</h3><FeatureSnapshotViewer :data="result.feature_snapshot" /></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import JsonEditor from '../components/JsonEditor.vue'
import RuleHitList from '../components/RuleHitList.vue'
import FeatureSnapshotViewer from '../components/FeatureSnapshotViewer.vue'
import RiskLevelTag from '../components/RiskLevelTag.vue'
import { checkRisk } from '../api/riskCheck'
import type { RiskCheckResult } from '../types/risk'

const eventTypes = ['order_create', 'order_pay', 'after_sale_apply', 'logistics_complaint']
const loading = ref(false)
const result = ref<RiskCheckResult | null>(null)
const form = ref({
  event_type: 'order_create',
  source_id: `REQ${Date.now()}`,
  user_id: 'U10001',
  order_id: 'O10001',
  event_payload: {
    order_amount: 5200,
    order_item_count: 25,
    payment_method: 'virtual_card',
    phone: '13800000000',
    device_id: 'D10001',
    ip: '10.10.1.1',
    address: '上海市浦东新区',
    user_register_days: 3,
    is_coupon_used: true,
    coupon_discount_rate: 0.6
  }
})

async function submit() {
  loading.value = true
  try {
    result.value = await checkRisk(form.value) as RiskCheckResult
    ElMessage.success('风险检查完成')
  } finally {
    loading.value = false
  }
}
</script>
