<template>
  <div class="page">
    <div class="page-title">
      <h2>运营看板</h2>
    </div>

    <div class="panel toolbar">
      <el-date-picker
        v-model="range"
        type="daterange"
        value-format="YYYY-MM-DD"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
      />
      <el-button type="primary" @click="load">查询</el-button>
      <el-button :loading="aiLoading" @click="loadAiAnalysis">AI 分析趋势</el-button>
    </div>

    <div class="metric-grid">
      <div class="metric"><div class="metric-label">风险事件总数</div><div class="metric-value">{{ data?.event_total || 0 }}</div></div>
      <div class="metric"><div class="metric-label">高风险占比</div><div class="metric-value">{{ Math.round((data?.high_risk_rate || 0) * 100) }}%</div></div>
      <div class="metric"><div class="metric-label">案件数</div><div class="metric-value">{{ data?.case_total || 0 }}</div></div>
      <div class="metric"><div class="metric-label">已处理案件</div><div class="metric-value">{{ data?.resolved_case_total || 0 }}</div></div>
      <div class="metric"><div class="metric-label">平均处理时长</div><div class="metric-value">{{ data?.avg_case_process_hours || 0 }}h</div></div>
      <div class="metric"><div class="metric-label">黑名单命中</div><div class="metric-value">{{ data?.blacklist_hit_count || 0 }}</div></div>
    </div>

    <div class="panel">
      <h3>风险事件趋势</h3>
      <div ref="trendRef" style="height: 300px" />
    </div>

    <div class="two-col">
      <div class="panel">
        <h3>风险等级分布</h3>
        <div ref="pieRef" style="height: 300px" />
      </div>
      <div class="panel">
        <h3>规则命中排行</h3>
        <div ref="barRef" style="height: 300px" />
      </div>
    </div>

    <div v-if="aiAnalysis" class="panel">
      <div class="panel-title">
        <h3>AI 趋势分析</h3>
        <el-tag type="info" size="small">LLM 辅助解读</el-tag>
      </div>
      <el-alert :title="aiAnalysis.summary" type="success" :closable="false" />
      <div class="analysis-grid">
        <div>
          <h4>关键洞察</h4>
          <ul>
            <li v-for="item in aiAnalysis.insights" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div>
          <h4>运营建议</h4>
          <ul>
            <li v-for="item in aiAnalysis.suggestions" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div>
          <h4>重点关注</h4>
          <el-tag v-for="item in aiAnalysis.risk_focus" :key="item" style="margin: 0 6px 6px 0">{{ item }}</el-tag>
          <span v-if="!aiAnalysis.risk_focus?.length">暂无</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getDashboard } from '../api/dashboard'
import { analyzeDashboardTrend } from '../api/aiRules'

const range = ref<[string, string] | null>(null)
const data = ref<any>(null)
const aiAnalysis = ref<any>(null)
const aiLoading = ref(false)
const pieRef = ref<HTMLElement>()
const barRef = ref<HTMLElement>()
const trendRef = ref<HTMLElement>()

async function load() {
  data.value = await getDashboard({ start_date: range.value?.[0], end_date: range.value?.[1] })
  await nextTick()
  renderCharts()
  await loadAiAnalysis()
}

async function loadAiAnalysis() {
  if (!data.value) return
  aiLoading.value = true
  try {
    aiAnalysis.value = await analyzeDashboardTrend({
      dashboard_data: data.value,
      start_date: range.value?.[0],
      end_date: range.value?.[1]
    })
  } finally {
    aiLoading.value = false
  }
}

function renderCharts() {
  // 渲染趋势图
  if (trendRef.value) {
    const trendData = data.value?.risk_event_trend || []
    echarts.init(trendRef.value).setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['总事件', '高风险'] },
      xAxis: { type: 'category', data: trendData.map((x: any) => x.date) },
      yAxis: { type: 'value' },
      series: [
        { name: '总事件', type: 'line', data: trendData.map((x: any) => x.total), smooth: true },
        { name: '高风险', type: 'line', data: trendData.map((x: any) => x.high_risk), smooth: true, itemStyle: { color: '#E6A23C' } }
      ]
    })
  }
  // 渲染饼图
  if (pieRef.value) {
    echarts.init(pieRef.value).setOption({
      tooltip: {},
      series: [{ type: 'pie', radius: '65%', data: data.value?.risk_level_distribution || [] }]
    })
  }
  // 渲染柱状图
  if (barRef.value) {
    const rows = data.value?.rule_hit_ranking || []
    echarts.init(barRef.value).setOption({
      tooltip: {},
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: rows.map((x: any) => x.rule_name) },
      series: [{ type: 'bar', data: rows.map((x: any) => x.hit_count) }]
    })
  }
}

onMounted(load)
</script>

<style scoped>
.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 14px;
}

.analysis-grid h4 {
  margin: 0 0 8px;
}

.analysis-grid ul {
  margin: 0;
  padding-left: 18px;
}

@media (max-width: 900px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}
</style>
