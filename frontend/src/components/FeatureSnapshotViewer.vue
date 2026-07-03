<template>
  <el-tabs v-model="tab">
    <el-tab-pane label="键值表" name="table">
      <el-table :data="rows" size="small" border max-height="320">
        <el-table-column prop="key" label="特征 Key" width="220" />
        <el-table-column prop="value" label="值" min-width="220" />
      </el-table>
    </el-tab-pane>
    <el-tab-pane label="JSON" name="json">
      <pre class="json-pre">{{ pretty }}</pre>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{ data?: Record<string, unknown> }>()
const tab = ref('table')

const rows = computed(() => Object.entries(props.data || {}).map(([key, value]) => ({ key, value: JSON.stringify(value) })))
const pretty = computed(() => JSON.stringify(props.data || {}, null, 2))
</script>

<style scoped>
.json-pre {
  max-height: 320px;
  margin: 0;
  padding: 12px;
  overflow: auto;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #f9fafb;
  font-family: Consolas, monospace;
}
</style>
