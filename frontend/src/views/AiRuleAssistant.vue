<template>
  <div class="page">
    <div class="page-title">
      <h2>AI 辅助规则</h2>
    </div>
    <el-alert
      title="AI 只生成规则草稿和辅助分析，保存前仍需系统校验和管理员确认，线上执行仍由规则引擎完成。"
      type="warning"
      :closable="false"
    />

    <div class="panel">
      <el-form label-width="90px">
        <el-form-item label="规则描述">
          <el-input v-model="description" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="期望分值">
          <el-input-number v-model="expectedScore" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="适用场景">
          <el-select v-model="scene">
            <el-option label="order_create" value="order_create" />
            <el-option label="order_pay" value="order_pay" />
            <el-option label="after_sale_apply" value="after_sale_apply" />
            <el-option label="logistics_complaint" value="logistics_complaint" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="generate">生成规则草稿</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div v-if="draft" class="two-col">
      <div class="panel">
        <h3>规则草稿</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="规则编码">{{ draft.rule_code }}</el-descriptions-item>
          <el-descriptions-item label="规则名称">{{ draft.rule_name }}</el-descriptions-item>
          <el-descriptions-item label="分值">{{ draft.score }}</el-descriptions-item>
          <el-descriptions-item label="优先级">{{ draft.priority }}</el-descriptions-item>
          <el-descriptions-item label="规则解释">{{ explanation }}</el-descriptions-item>
        </el-descriptions>
        <div class="action-row">
          <el-button @click="validate">校验</el-button>
          <el-button @click="runOverlap">重叠检测</el-button>
          <el-button @click="runTestCases">生成测试样例</el-button>
          <el-button type="primary" @click="save">保存为规则</el-button>
        </div>
        <el-alert
          v-if="validation"
          :title="validation.passed ? '校验通过' : validation.errors.join('; ')"
          :type="validation.passed ? 'success' : 'error'"
          style="margin-top: 12px"
        />
        <el-alert
          v-if="validation?.warnings?.length"
          :title="validation.warnings.join('；')"
          type="warning"
          style="margin-top: 12px"
        />
      </div>

      <div class="panel">
        <h3>条件 JSON</h3>
        <JsonEditor v-model="draft.condition_json" :rows="13" />
      </div>
    </div>

    <div v-if="overlap" class="panel">
      <h3>规则重叠检测</h3>
      <el-alert :title="overlap.summary" :type="overlap.overlaps?.length ? 'warning' : 'success'" :closable="false" />
      <el-table v-if="overlap.overlaps?.length" :data="overlap.overlaps" size="small" border style="margin-top: 12px">
        <el-table-column prop="rule_code" label="规则编码" width="180" />
        <el-table-column prop="rule_name" label="规则名称" min-width="180" />
        <el-table-column prop="priority" label="优先级" width="90" />
        <el-table-column prop="score" label="分值" width="90" />
        <el-table-column prop="relation" label="重叠关系" width="190" />
        <el-table-column prop="suggestion" label="建议" min-width="260" />
      </el-table>
    </div>

    <div v-if="testCases" class="panel">
      <h3>规则测试样例</h3>
      <el-table :data="testCases.cases" size="small" border>
        <el-table-column prop="name" label="样例" width="140" />
        <el-table-column prop="description" label="说明" width="220" />
        <el-table-column prop="event_type" label="事件类型" width="170" />
        <el-table-column label="事件参数" min-width="320">
          <template #default="{ row }">
            <pre class="json-preview">{{ JSON.stringify(row.event_payload, null, 2) }}</pre>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import JsonEditor from '../components/JsonEditor.vue'
import {
  analyzeRuleOverlap,
  explainAiRule,
  generateAiRule,
  generateRuleTestCases,
  validateAiRule
} from '../api/aiRules'
import { createRule } from '../api/rules'

const description = ref('注册 7 天内的新用户，如果订单金额大于 3000 元，则增加 35 分风险分')
const expectedScore = ref(35)
const scene = ref('order_create')
const loading = ref(false)
const draft = ref<any>(null)
const explanation = ref('')
const validation = ref<any>(null)
const overlap = ref<any>(null)
const testCases = ref<any>(null)

async function generate() {
  loading.value = true
  overlap.value = null
  testCases.value = null
  try {
    draft.value = await generateAiRule({ description: description.value, expected_score: expectedScore.value, scene: scene.value })
    validation.value = draft.value.validation
    const exp: any = await explainAiRule({ condition_json: draft.value.condition_json })
    explanation.value = exp.explanation
  } finally {
    loading.value = false
  }
}

async function validate() {
  validation.value = await validateAiRule({
    condition_json: draft.value.condition_json,
    score: draft.value.score,
    priority: draft.value.priority
  })
}

async function runOverlap() {
  overlap.value = await analyzeRuleOverlap({
    condition_json: draft.value.condition_json,
    rule_code: draft.value.rule_code
  })
}

async function runTestCases() {
  testCases.value = await generateRuleTestCases({
    condition_json: draft.value.condition_json,
    scene: scene.value
  })
}

async function save() {
  await validate()
  if (!validation.value?.passed) return
  await createRule(draft.value)
  ElMessage.success('规则已保存')
}
</script>

<style scoped>
.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.json-preview {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
