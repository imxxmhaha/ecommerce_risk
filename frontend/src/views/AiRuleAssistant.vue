<template>
  <div class="page">
    <div class="page-title"><h2>AI 辅助规则</h2></div>
    <el-alert title="AI 只生成规则草稿，保存前必须经过系统校验和管理员确认，线上仍由规则引擎执行。" type="warning" :closable="false" />
    <div class="panel">
      <el-form label-width="90px">
        <el-form-item label="规则描述"><el-input v-model="description" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="期望分值"><el-input-number v-model="expectedScore" :min="0" :max="100" /></el-form-item>
        <el-form-item label="适用场景"><el-select v-model="scene"><el-option label="order_create" value="order_create" /><el-option label="order_pay" value="order_pay" /></el-select></el-form-item>
        <el-form-item><el-button type="primary" :loading="loading" @click="generate">生成规则草稿</el-button></el-form-item>
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
          <el-descriptions-item label="解释">{{ explanation }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <div class="panel">
        <h3>条件 JSON</h3>
        <JsonEditor v-model="draft.condition_json" :rows="10" />
        <div style="margin-top: 12px"><el-button @click="validate">校验</el-button><el-button type="primary" @click="save">保存为规则</el-button></div>
        <el-alert v-if="validation" :title="validation.passed ? '校验通过' : validation.errors.join('; ')" :type="validation.passed ? 'success' : 'error'" style="margin-top: 12px" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import JsonEditor from '../components/JsonEditor.vue'
import { explainAiRule, generateAiRule, validateAiRule } from '../api/aiRules'
import { createRule } from '../api/rules'

const description = ref('注册 7 天内的新用户，如果订单金额大于 3000 元，则增加 35 分风险分')
const expectedScore = ref(35)
const scene = ref('order_create')
const loading = ref(false)
const draft = ref<any>(null)
const explanation = ref('')
const validation = ref<any>(null)

async function generate() {
  loading.value = true
  try {
    draft.value = await generateAiRule({ description: description.value, expected_score: expectedScore.value, scene: scene.value })
    validation.value = draft.value.validation
    const exp: any = await explainAiRule({ condition_json: draft.value.condition_json })
    explanation.value = exp.explanation
  } finally { loading.value = false }
}
async function validate() { validation.value = await validateAiRule({ condition_json: draft.value.condition_json, score: draft.value.score, priority: draft.value.priority }) }
async function save() {
  await validate()
  if (!validation.value?.passed) return
  await createRule(draft.value)
  ElMessage.success('规则已保存')
}
</script>
