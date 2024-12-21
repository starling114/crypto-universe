<template>
  <div>
    <cu-label v-if="label" :name="name" :label="label" :tooltip="tooltip" />
    <textarea :id="name" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder || ''" :rows="rows"
      class="mb-2 bg-white whitespace-nowrap border border-gray-300 text-gray-900 rounded-lg focus:ring-gray-600 focus:border-gray-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-white dark:focus:border-white" />
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { CuLabel } from '@/components/cu'

defineProps({
  name: { type: String, required: true },
  modelValue: { type: [String, Number, null], required: true },
  label: { type: String },
  tooltip: { type: String },
  placeholder: { type: String },
  rows: { type: Number, default: 6 }
})
</script>
