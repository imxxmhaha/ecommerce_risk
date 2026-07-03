<template>
  <el-table :data="items" size="small" border>
    <el-table-column prop="rule_code" label="规则编码" width="180" />
    <el-table-column prop="rule_name" label="规则名称" width="180" />
    <el-table-column prop="priority" label="优先级" width="90" />
    <el-table-column prop="hit_score" label="分值" width="90" />
    <el-table-column label="最终生效" width="110">
      <template #default="{ row }">
        <el-tag v-if="row.is_effective" type="success" size="small">最终</el-tag>
        <span v-else>-</span>
      </template>
    </el-table-column>
    <el-table-column prop="hit_message" label="命中原因" min-width="220" />
  </el-table>
</template>

<script setup lang="ts">
import type { RuleHit } from '../types/risk'

defineProps<{ items: RuleHit[] }>()
</script>
