<template>
  <div>
    <el-input
      v-model="text"
      type="textarea"
      :rows="rows"
      class="json-editor"
      @blur="emitIfValid"
    />
    <div class="json-actions">
      <el-button size="small" @click="formatJson">格式化</el-button>
      <span v-if="error" class="error">{{ error }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{ modelValue: any; rows?: number }>(), { rows: 8 })
const emit = defineEmits<{ 'update:modelValue': [value: any] }>()

const text = ref(JSON.stringify(props.modelValue || {}, null, 2))
const error = ref('')

watch(() => props.modelValue, (value) => {
  text.value = JSON.stringify(value || {}, null, 2)
})

function emitIfValid() {
  try {
    const parsed = JSON.parse(text.value || '{}')
    error.value = ''
    emit('update:modelValue', parsed)
  } catch (err: any) {
    error.value = err.message
  }
}

function formatJson() {
  emitIfValid()
  if (!error.value) text.value = JSON.stringify(JSON.parse(text.value || '{}'), null, 2)
}
</script>

<style scoped>
.json-editor :deep(textarea) {
  font-family: Consolas, monospace;
}

.json-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.error {
  color: #dc2626;
  font-size: 13px;
}
</style>
