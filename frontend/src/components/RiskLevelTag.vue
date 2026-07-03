<template>
  <el-tag :type="tagType" effect="light">{{ label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ level?: string }>()

const label = computed(() => {
  const map: Record<string, string> = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[props.level || ''] || props.level || '-'
})

const tagType = computed(() => {
  if (props.level === 'low') return 'success'
  if (props.level === 'medium') return 'warning'
  if (props.level === 'high') return 'danger'
  return 'info'
})
</script>
