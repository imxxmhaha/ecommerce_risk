<template>
  <div class="page">
    <div class="page-title"><h2>运营看板</h2></div>
    <div class="panel toolbar">
      <el-date-picker v-model="range" type="daterange" value-format="YYYY-MM-DD" start-placeholder="开始日期" end-placeholder="结束日期" />
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    <div class="metric-grid">
      <div class="metric"><div class="metric-label">风险事件总数</div><div class="metric-value">{{ data?.event_total || 0 }}</div></div>
      <div class="metric"><div class="metric-label">高风险占比</div><div class="metric-value">{{ Math.round((data?.high_risk_rate || 0) * 100) }}%</div></div>
      <div class="metric"><div class="metric-label">案件数</div><div class="metric-value">{{ data?.case_total || 0 }}</div></div>
      <div class="metric"><div class="metric-label">黑名单命中</div><div class="metric-value">{{ data?.blacklist_hit_count || 0 }}</div></div>
    </div>
    <div class="two-col">
      <div class="panel"><h3>风险等级分布</h3><div ref="pieRef" style="height: 300px" /></div>
      <div class="panel"><h3>规则命中排行</h3><div ref="barRef" style="height: 300px" /></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getDashboard } from '../api/dashboard'

const range = ref<[string, string] | null>(null)
const data = ref<any>(null)
const pieRef = ref<HTMLElement>()
const barRef = ref<HTMLElement>()

async function load() {
  data.value = await getDashboard({ start_date: range.value?.[0], end_date: range.value?.[1] })
  await nextTick()
  renderCharts()
}
function renderCharts() {
  if (pieRef.value) {
    echarts.init(pieRef.value).setOption({ tooltip: {}, series: [{ type: 'pie', radius: '65%', data: data.value?.risk_level_distribution || [] }] })
  }
  if (barRef.value) {
    const rows = data.value?.rule_hit_ranking || []
    echarts.init(barRef.value).setOption({ tooltip: {}, xAxis: { type: 'value' }, yAxis: { type: 'category', data: rows.map((x: any) => x.rule_name) }, series: [{ type: 'bar', data: rows.map((x: any) => x.hit_count) }] })
  }
}
onMounted(load)
</script>
