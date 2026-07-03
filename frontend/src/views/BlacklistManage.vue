<template>
  <div class="page">
    <div class="page-title"><h2>黑名单管理</h2><el-button type="primary" @click="openCreate">新增黑名单</el-button></div>
    <div class="panel toolbar">
      <el-select v-model="query.blacklist_type" placeholder="类型" clearable style="width: 160px">
        <el-option v-for="x in types" :key="x" :label="x" :value="x" />
      </el-select>
      <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px"><el-option label="active" value="active" /><el-option label="deleted" value="deleted" /></el-select>
      <el-input v-model="query.keyword" placeholder="命中值" style="width: 220px" />
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    <div class="panel">
      <el-table :data="rows" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="blacklist_type" label="类型" width="140" />
        <el-table-column prop="blacklist_value" label="命中值" min-width="180" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="100"><template #default="{ row }"><el-button link type="danger" @click="remove(row)">删除</el-button></template></el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="dialogVisible" title="新增黑名单" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="类型"><el-select v-model="form.blacklist_type"><el-option v-for="x in types" :key="x" :label="x" :value="x" /></el-select></el-form-item>
        <el-form-item label="命中值"><el-input v-model="form.blacklist_value" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createBlacklist, deleteBlacklist, listBlacklists } from '../api/blacklists'

const types = ['user_id', 'phone', 'address', 'device_id', 'ip', 'order_id']
const query = ref({ blacklist_type: '', status: 'active', keyword: '', page: 1, page_size: 20 })
const rows = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = ref({ blacklist_type: 'user_id', blacklist_value: '', remark: '' })
async function load() { loading.value = true; try { const res: any = await listBlacklists(query.value); rows.value = res.items || [] } finally { loading.value = false } }
function openCreate() { form.value = { blacklist_type: 'user_id', blacklist_value: '', remark: '' }; dialogVisible.value = true }
async function save() { await createBlacklist(form.value); ElMessage.success('保存成功'); dialogVisible.value = false; load() }
async function remove(row: any) { await ElMessageBox.confirm('确认删除该黑名单？'); await deleteBlacklist({ id: row.id }); load() }
onMounted(load)
</script>
