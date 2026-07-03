<template>
  <el-tag :type="tagType" effect="light">{{ label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status?: string }>()

const label = computed(() => {
  const map: Record<string, string> = {
    pending: '待处理',
    reviewing: '审核中',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[props.status || ''] || props.status || '-'
})

const tagType = computed(() => {
  if (props.status === 'pending') return 'warning'
  if (props.status === 'reviewing') return 'primary'
  if (props.status === 'approved') return 'success'
  if (props.status === 'rejected') return 'danger'
  return 'info'
})
</script>
