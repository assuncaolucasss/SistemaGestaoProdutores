<template>
  <div>
    <div class="text-xs text-gray-400 mb-1">{{ label }}</div>
    <input
      v-if="editing"
      :type="type || 'text'"
      :value="modelValue"
      @input="$emit('update:modelValue', applyUpper($event.target.value))"
      :class="[
        'w-full px-3 py-2 border border-primary-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-600 box-border',
        shouldUpper ? 'uppercase' : ''
      ]"
    />
    <div v-else :class="['text-gray-700', shouldUpper ? 'uppercase' : '']">
      {{ value || '—' }}
    </div>
  </div>
</template>

<script setup>
const props = defineProps(['label', 'editing', 'modelValue', 'value', 'type'])
defineEmits(['update:modelValue'])

const SKIP_UPPER = ['date', 'number', 'email']
const shouldUpper = !SKIP_UPPER.includes(props.type)

function applyUpper(val) {
  return shouldUpper ? val.toUpperCase() : val
}
</script>
