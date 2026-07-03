<template>
  <div class="page">
    <div class="page-title">
      <h2>规则管理</h2>
      <div><el-button @click="$router.push('/ai-rules')">AI生成规则</el-button><el-button type="primary" @click="openCreate">新增规则</el-button></div>
    </div>
    <div class="panel toolbar">
      <el-select v-model="query.rule_status" placeholder="规则状态" clearable style="width: 160px"><el-option label="启用" value="enabled" /><el-option label="停用" value="disabled" /></el-select>
      <el-input v-model="query.keyword" placeholder="规则名称/编码" style="width: 240px" />
      <el-button type="primary" @click="load">查询</el-button>
      <el-button @click="reset">重置</el-button>
    </div>
    <div class="panel">
      <el-table :data="rows" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="rule_name" label="规则名称" min-width="160" />
        <el-table-column prop="rule_code" label="规则编码" min-width="180" />
        <el-table-column prop="rule_status" label="状态" width="100" />
        <el-table-column prop="priority" label="优先级" width="90" />
        <el-table-column prop="score" label="分值" width="90" />
        <el-table-column prop="hit_count" label="命中次数" width="110" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link @click="toggle(row)">{{ row.rule_status === 'enabled' ? '停用' : '启用' }}</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="dialogVisible" :title="editing ? '编辑规则' : '新增规则'" width="760px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="规则编码"><el-input v-model="form.rule_code" /></el-form-item>
        <el-form-item label="规则名称"><el-input v-model="form.rule_name" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.rule_status"><el-option label="启用" value="enabled" /><el-option label="停用" value="disabled" /></el-select></el-form-item>
        <el-form-item label="优先级"><el-input-number v-model="form.priority" :min="0" /></el-form-item>
        <el-form-item label="分值"><el-input-number v-model="form.score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="条件JSON"><JsonEditor v-model="form.condition_json" :rows="8" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import JsonEditor from '../components/JsonEditor.vue'
import { createRule, deleteRule, listRules, setRuleStatus, updateRule } from '../api/rules'

const loading = ref(false)
const rows = ref<any[]>([])
const query = ref({ rule_status: '', keyword: '', page: 1, page_size: 20 })
const dialogVisible = ref(false)
const editing = ref(false)
const form = ref<any>({})

function defaultForm() {
  return { rule_code: '', rule_name: '', rule_status: 'enabled', priority: 100, score: 10, condition_json: { operator: '>', feature: 'order_amount', value: 1000 }, description: '' }
}
async function load() { loading.value = true; try { const res: any = await listRules(query.value); rows.value = res.items || [] } finally { loading.value = false } }
function reset() { query.value.rule_status = ''; query.value.keyword = ''; load() }
function openCreate() { editing.value = false; form.value = defaultForm(); dialogVisible.value = true }
function openEdit(row: any) { editing.value = true; form.value = JSON.parse(JSON.stringify(row)); dialogVisible.value = true }
async function save() { editing.value ? await updateRule(form.value) : await createRule(form.value); ElMessage.success('保存成功'); dialogVisible.value = false; load() }
async function toggle(row: any) { await setRuleStatus({ id: row.id, rule_status: row.rule_status === 'enabled' ? 'disabled' : 'enabled' }); load() }
async function remove(row: any) { await ElMessageBox.confirm('确认删除该规则？'); await deleteRule({ id: row.id }); load() }
onMounted(load)
</script>
