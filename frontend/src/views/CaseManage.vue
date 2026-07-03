<template>
  <div class="page">
    <div class="page-title"><h2>案件管理</h2></div>
    <div class="panel toolbar">
      <el-select v-model="query.case_status" placeholder="案件状态" clearable style="width: 160px">
        <el-option label="待处理" value="pending" /><el-option label="已通过" value="approved" /><el-option label="已拒绝" value="rejected" />
      </el-select>
      <el-input v-model="query.user_id" placeholder="用户编号" style="width: 180px" />
      <el-input v-model="query.order_id" placeholder="订单编号" style="width: 180px" />
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    <div class="panel">
      <el-table :data="rows" border v-loading="loading">
        <el-table-column prop="id" label="案件编号" width="100" />
        <el-table-column label="状态" width="110"><template #default="{ row }"><CaseStatusTag :status="row.case_status" /></template></el-table-column>
        <el-table-column prop="user_id" label="用户" />
        <el-table-column prop="order_id" label="订单" />
        <el-table-column prop="reviewer_id" label="审核人" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="120"><template #default="{ row }"><el-button link type="primary" @click="$router.push(`/cases/${row.id}`)">查看</el-button></template></el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import CaseStatusTag from '../components/CaseStatusTag.vue'
import { listCases } from '../api/cases'

const loading = ref(false)
const rows = ref<any[]>([])
const query = ref({ case_status: '', user_id: '', order_id: '', page: 1, page_size: 20 })
async function load() { loading.value = true; try { const res: any = await listCases(query.value); rows.value = res.items || [] } finally { loading.value = false } }
onMounted(load)
</script>
