<template>
  <div class="page">
    <div class="page-title">
      <h2>案件详情 #{{ caseId }}</h2>
      <el-button @click="$router.push('/cases')">返回列表</el-button>
    </div>

    <div v-if="detail" class="metric-grid">
      <div class="metric"><div class="metric-label">案件状态</div><div class="metric-value"><CaseStatusTag :status="detail.case.case_status" /></div></div>
      <div class="metric"><div class="metric-label">风险评分</div><div class="metric-value">{{ detail.assessment?.risk_score }}</div></div>
      <div class="metric"><div class="metric-label">风险等级</div><div class="metric-value"><RiskLevelTag :level="detail.assessment?.risk_level" /></div></div>
      <div class="metric"><div class="metric-label">处理建议</div><div class="metric-value">{{ detail.assessment?.decision }}</div></div>
    </div>

    <div v-if="detail" class="panel">
      <div class="panel-title">
        <h3>AI 风险解释</h3>
        <el-button :loading="aiLoading" @click="loadAiExplain">重新生成</el-button>
      </div>
      <el-skeleton v-if="aiLoading && !aiExplain" :rows="3" animated />
      <el-descriptions v-else-if="aiExplain" :column="1" border>
        <el-descriptions-item label="风险摘要">{{ aiExplain.summary }}</el-descriptions-item>
        <el-descriptions-item label="最终规则">{{ aiExplain.effective_rule_explanation }}</el-descriptions-item>
        <el-descriptions-item label="审核建议">{{ aiExplain.review_suggestion }}</el-descriptions-item>
        <el-descriptions-item label="关键证据">
          <el-tag v-for="item in aiExplain.key_evidence" :key="item" style="margin: 0 6px 6px 0">{{ item }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <el-empty v-else description="暂无 AI 解释" />
    </div>

    <div v-if="detail" class="two-col">
      <div class="panel"><h3>命中规则</h3><RuleHitList :items="detail.rule_hits" /></div>
      <div class="panel"><h3>特征快照</h3><FeatureSnapshotViewer :data="detail.feature_snapshot" /></div>
    </div>

    <div v-if="detail" class="panel">
      <h3>审核日志</h3>
      <el-timeline>
        <el-timeline-item v-for="log in detail.review_logs" :key="log.id" :timestamp="log.created_at">
          {{ log.operator_id }} {{ log.action_type }}：{{ log.action_remark }}
        </el-timeline-item>
      </el-timeline>
    </div>

    <div class="panel">
      <h3>审核操作</h3>
      <el-alert
        v-if="!isPending"
        :title="`案件已审核，当前状态：${statusText}`"
        type="warning"
        show-icon
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-form label-width="90px">
        <el-form-item label="审核结论">
          <el-select v-model="review.review_result" placeholder="请选择" :disabled="!isPending">
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核备注">
          <el-input v-model="review.review_remark" type="textarea" :disabled="!isPending" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitReview" :disabled="!isPending">提交审核</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import CaseStatusTag from '../components/CaseStatusTag.vue'
import RiskLevelTag from '../components/RiskLevelTag.vue'
import RuleHitList from '../components/RuleHitList.vue'
import FeatureSnapshotViewer from '../components/FeatureSnapshotViewer.vue'
import { getCaseDetail, reviewCase } from '../api/cases'
import { explainRiskCase } from '../api/aiRules'

const route = useRoute()
const caseId = route.params.caseId as string
const detail = ref<any>(null)
const aiExplain = ref<any>(null)
const aiLoading = ref(false)
const review = ref({ case_id: Number(caseId), review_result: '', review_remark: '' })

const statusMap: Record<string, string> = { pending: '待处理', approved: '已通过', rejected: '已拒绝' }
const isPending = computed(() => detail.value?.case?.case_status === 'pending')
const statusText = computed(() => statusMap[detail.value?.case?.case_status] || detail.value?.case?.case_status)

async function load() {
  detail.value = await getCaseDetail(caseId)
  if (detail.value?.case?.case_status && detail.value.case.case_status !== 'pending') {
    review.value.review_result = detail.value.case.case_status
  } else {
    review.value.review_result = ''
  }
  await loadAiExplain()
}

async function loadAiExplain() {
  if (!detail.value) return
  aiLoading.value = true
  try {
    aiExplain.value = await explainRiskCase({
      assessment: detail.value.assessment || {},
      rule_hits: detail.value.rule_hits || [],
      feature_snapshot: detail.value.feature_snapshot || {}
    })
  } finally {
    aiLoading.value = false
  }
}

async function submitReview() {
  await reviewCase(review.value)
  ElMessage.success('审核已提交')
  load()
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
</style>
